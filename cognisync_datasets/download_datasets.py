"""
Cognisync - dataset downloader (approved shortlist).

Run on your own machine (needs internet):
    pip install huggingface_hub kaggle requests
    python download_datasets.py                          # the six approved sources
    python download_datasets.py --optional llm_aggrefact # gated, evaluation-only
    python download_datasets.py --only oulad kaggle_lifestyle

Kaggle needs an API token at ~/.kaggle/kaggle.json (Kaggle > Settings > Create New Token).
LLM-AggreFact is gated: accept its terms on the Hugging Face page, then `huggingface-cli login`.

Every download is recorded in data/raw/MANIFEST.json with the URL actually used,
UTC date and SHA-256 per file (Phase 1 data card requirement).
"""
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path("data/raw")
MANIFEST = ROOT / "MANIFEST.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def record(name, source, folder: Path, licence, note=""):
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    manifest[name] = {
        "source": source,
        "licence": licence,
        "downloaded_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "folder": str(folder),
        "files_sha256": {
            str(p.relative_to(folder)): sha256(p)
            for p in sorted(folder.rglob("*"))
            if p.is_file() and ".git" not in p.parts
        },
        "note": note,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2))


def http_get(url: str, dest: Path):
    import requests

    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)


def hf_snapshot(repo_id: str, dest: Path, repo_type="dataset", **kw):
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=repo_id, repo_type=repo_type, local_dir=dest, **kw)


def unzip(zpath: Path, dest: Path):
    if not zipfile.is_zipfile(zpath):  # a moved URL may return an HTML page instead
        raise ValueError(f"{zpath} is not a zip file")
    zipfile.ZipFile(zpath).extractall(dest)


# --------------------------------------------------------------------------- #
# Approved datasets
# --------------------------------------------------------------------------- #

def kaggle_lifestyle():
    """A2 global prior only. 2,000 rows, single snapshot per student, GPA target."""
    dest = ROOT / "kaggle_student_lifestyle"
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["kaggle", "datasets", "download", "-d",
         "steve1215rogg/student-lifestyle-dataset", "-p", str(dest), "--unzip"],
        check=True,
    )
    record("kaggle_lifestyle",
           "https://www.kaggle.com/datasets/steve1215rogg/student-lifestyle-dataset",
           dest, "Apache 2.0",
           "GPA is NOT retention or next-test score. Stress_Level is derived from "
           "study and sleep hours (per Kaggle description): leakage risk. Provenance "
           "not stated; treat as possibly synthetic. Check whether daily hours sum to 24.")


def oulad():
    """B1 scores-only baselines and B3 calibration comparison."""
    dest = ROOT / "oulad"
    zpath = dest / "oulad.zip"
    urls = [
        "https://archive.ics.uci.edu/static/public/349/"
        "open+university+learning+analytics+dataset.zip",
        "http://schools.stem.open.ac.uk/cdn/files/anonymisedData.zip",  # 404 as of 2026-11
    ]
    for url in urls:
        try:
            http_get(url, zpath)
            unzip(zpath, dest)
            break
        except Exception as e:  # noqa: BLE001
            print(f"  {url} failed ({e})")
    else:
        raise RuntimeError("all OULAD URLs failed")
    record("oulad", url, dest, "CC BY 4.0 (per UCI listing)",
           "studentAssessment.csv (score 0-100, date_submitted) for B1/B3; "
           "studentVle.csv daily clicks = study-behaviour proxy, NOT lifestyle.")


def duolingo_hlr():
    """A2 retention: p_recall after delta seconds (measured delayed recall)."""
    dest = ROOT / "duolingo_hlr"
    zpath = dest / "dataverse.zip"
    # Dataverse bulk-download endpoint for the whole dataset (data is not in the GitHub repo)
    url = ("https://dataverse.harvard.edu/api/access/dataset/:persistentId/"
           "?persistentId=doi:10.7910/DVN/N8XJME")
    http_get(url, zpath)
    unzip(zpath, dest)
    zpath.unlink()
    record("duolingo_hlr", url, dest, "CHECK Dataverse page (code is MIT)",
           "UTC unix timestamps, no user timezone: cannot validate time-of-day (A3).")


def sciq():
    """A4 quiz/RAG testing: 13.7K science MCQs with support passages."""
    dest = ROOT / "sciq"
    hf_snapshot("allenai/sciq", dest)
    record("sciq", "https://huggingface.co/datasets/allenai/sciq", dest, "CC BY-NC 3.0")


def devaraj_factuality():
    """B2: human-annotated factual errors in simplifications."""
    dest = ROOT / "devaraj_simplification_factuality"
    subprocess.run(["git", "clone", "--depth", "1",
                    "https://github.com/AshOlogn/Evaluating-Factuality-in-Text-Simplification",
                    str(dest)], check=True)
    print("  Some annotations are only in the Google Drive folder linked from the "
          "README - download them into this folder by hand.")
    record("devaraj",
           "https://github.com/AshOlogn/Evaluating-Factuality-in-Text-Simplification",
           dest, "No licence in repo - ask authors before redistributing",
           "News/Wikipedia domain, not textbooks.")


def nli_model():
    """B2: pretrained NLI model, used as-is (not trained)."""
    dest = Path("models/deberta-v3-base-mnli-fever-anli")
    repo = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
    # keep model.safetensors only; skip duplicate PyTorch/TF/Flax/ONNX copies of the weights
    hf_snapshot(repo, dest, repo_type="model",
                ignore_patterns=["*.bin", "*.h5", "*.msgpack", "*.onnx", "onnx/*", "tf_model*"])
    record("nli_model", f"https://huggingface.co/{repo}", dest, "MIT")


# --------------------------------------------------------------------------- #
# Optional
# --------------------------------------------------------------------------- #

def llm_aggrefact():
    dest = ROOT / "llm_aggrefact"
    hf_snapshot("lytang/LLM-AggreFact", dest)  # gated: accept terms + login first
    record("llm_aggrefact", "https://huggingface.co/datasets/lytang/LLM-AggreFact",
           dest, "CC BY-ND 4.0, evaluation only (no training/fine-tuning)",
           "Use only to sanity-check the NLI-only baseline.")


def studentlife():
    print("  StudentLife (~5 GB) is a manual download: "
          "https://studentlife.cs.dartmouth.edu/dataset.html")


CORE = {
    "kaggle_lifestyle": kaggle_lifestyle,
    "oulad": oulad,
    "duolingo_hlr": duolingo_hlr,
    "sciq": sciq,
    "devaraj": devaraj_factuality,
    "nli_model": nli_model,
}
OPTIONAL = {
    "llm_aggrefact": llm_aggrefact,
    "studentlife": studentlife,
}
ALL = {**CORE, **OPTIONAL}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", choices=list(ALL), help="run just these")
    ap.add_argument("--optional", nargs="+", choices=list(OPTIONAL), default=[],
                    help="add optional sources to the core six")
    args = ap.parse_args()

    names = args.only or list(CORE) + args.optional
    ROOT.mkdir(parents=True, exist_ok=True)
    failed = []
    for name in names:
        print(f"==> {name}")
        try:
            ALL[name]()
        except Exception as e:  # noqa: BLE001
            print(f"  FAILED: {e}")
            failed.append(name)
    print("\nDone. Manifest:", MANIFEST)
    if failed:
        print("Failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
