import csv
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import requests
from latch.executions import rename_current_execution, report_nextflow_used_storage
from latch.ldata.path import LPath
from latch.resources.tasks import custom_task, nextflow_runtime_task
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.nextflow.workflow import get_flag
from latch_cli.services.register.utils import import_module_by_path
from latch_cli.utils import urljoins

from wf.enums import (
    AnnotationTool,
    Assembler,
    AssemblyType,
    BaktaDbDownloadArgs,
    CanuMode,
    PolishMethod,
)

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata


@dataclass(frozen=True)
class SampleSheet:
    sampleid: str
    forwardreads: LatchFile
    reversereads: Optional[LatchFile]
    run: Optional[str]


@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize(run_name: str) -> str:
    rename_current_execution(str(run_name))

    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "storage_expiration_hours": 0,
            "version": 2,
        },
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]


def custom_samplesheet_constructor(
    samples: List[SampleSheet], shared_dir: Path
) -> Path:
    samplesheet = Path(shared_dir / "samplesheet.csv")
    columns = ["sampleID", "forwardReads", "reverseReads", "run"]

    with open(samplesheet, "w") as f:
        writer = csv.DictWriter(f, columns, delimiter=",")
        writer.writeheader()

        for sample in samples:
            forward_reads_local_path = Path(sample.forwardreads.local_path)
            forward_reads_shared_path = shared_dir / forward_reads_local_path.name
            shutil.move(str(forward_reads_local_path), str(forward_reads_shared_path))

            reverse_reads_shared_path = ""
            if sample.reversereads:
                reverse_reads_local_path = Path(sample.reversereads.local_path)
                reverse_reads_shared_path = shared_dir / reverse_reads_local_path.name
                shutil.move(
                    str(reverse_reads_local_path), str(reverse_reads_shared_path)
                )

            row_data = {
                "sampleID": sample.sampleid,
                "forwardReads": str(forward_reads_shared_path),
                "reverseReads": str(reverse_reads_shared_path)
                if reverse_reads_shared_path
                else "",
                "run": sample.run if sample.run else "",
            }
            writer.writerow(row_data)

    return samplesheet


@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(
    pvc_name: str,
    run_name: str,
    input: str,
    outdir: LatchOutputDir,
    email: Optional[str],
    fastp_args: Optional[str],
    save_trimmed: bool,
    save_trimmed_fail: bool,
    save_merged: bool,
    skip_fastqc: bool,
    skip_fastp: bool,
    kraken2db: Optional[LatchFile],
    kmerfinderdb: Optional[LatchFile],
    reference_fasta: Optional[LatchFile],
    reference_gff: Optional[LatchFile],
    ncbi_assembly_metadata: Optional[LatchFile],
    unicycler_args: Optional[str],
    canu_mode: Optional[str],
    canu_args: Optional[str],
    dragonflye_args: Optional[str],
    prokka_args: Optional[str],
    baktadb: Optional[LatchFile],
    baktadb_download: bool,
    skip_kraken2: bool,
    skip_kmerfinder: bool,
    skip_annotation: bool,
    skip_pycoqc: bool,
    skip_polish: bool,
    skip_multiqc: bool,
    multiqc_title: Optional[str],
    multiqc_methods_description: Optional[str],
    assembler: Optional[str],
    assembly_type: Optional[str],
    polish_method: Optional[str],
    annotation_tool: Optional[str],
    baktadb_download_args: Optional[str],
    dfast_config: Optional[str],
) -> None:
    shared_dir = Path("/nf-workdir")

    input_samplesheet = custom_samplesheet_constructor(input, shared_dir)

    ignore_list = [
        "latch",
        ".latch",
        ".git",
        "nextflow",
        ".nextflow",
        "work",
        "results",
        "miniconda",
        "anaconda3",
        "mambaforge",
    ]

    shutil.copytree(
        Path("/root"),
        shared_dir,
        ignore=lambda src, names: ignore_list,
        ignore_dangling_symlinks=True,
        dirs_exist_ok=True,
    )

    cmd = [
        "/root/nextflow",
        "run",
        str(shared_dir / "main.nf"),
        "-work-dir",
        str(shared_dir),
        "-profile",
        "docker",
        "-c",
        "latch.config",
        "-resume",
        *get_flag("input", input_samplesheet),
        *get_flag("outdir", LatchOutputDir(f"{outdir.remote_path}/{run_name}")),
        *get_flag("email", email),
        *get_flag("fastp_args", fastp_args),
        *get_flag("save_trimmed", save_trimmed),
        *get_flag("save_trimmed_fail", save_trimmed_fail),
        *get_flag("save_merged", save_merged),
        *get_flag("skip_fastqc", skip_fastqc),
        *get_flag("skip_fastp", skip_fastp),
        *get_flag("kraken2db", kraken2db),
        *get_flag("kmerfinderdb", kmerfinderdb),
        *get_flag("reference_fasta", reference_fasta),
        *get_flag("reference_gff", reference_gff),
        *get_flag("ncbi_assembly_metadata", ncbi_assembly_metadata),
        *get_flag("assembler", assembler),
        *get_flag("assembly_type", assembly_type),
        *get_flag("unicycler_args", unicycler_args),
        *get_flag("canu_mode", canu_mode),
        *get_flag("canu_args", canu_args),
        *get_flag("dragonflye_args", dragonflye_args),
        *get_flag("polish_method", polish_method),
        *get_flag("annotation_tool", annotation_tool),
        *get_flag("prokka_args", prokka_args),
        *get_flag("baktadb", baktadb),
        *get_flag("baktadb_download", baktadb_download),
        *get_flag("baktadb_download_args", baktadb_download_args),
        *get_flag("dfast_config", dfast_config),
        *get_flag("skip_kraken2", skip_kraken2),
        *get_flag("skip_kmerfinder", skip_kmerfinder),
        *get_flag("skip_annotation", skip_annotation),
        *get_flag("skip_pycoqc", skip_pycoqc),
        *get_flag("skip_polish", skip_polish),
        *get_flag("skip_multiqc", skip_multiqc),
        *get_flag("multiqc_title", multiqc_title),
        *get_flag("multiqc_methods_description", multiqc_methods_description),
    ]

    print("Launching Nextflow Runtime")
    print(" ".join(cmd))
    print(flush=True)

    failed = False
    try:
        env = {
            **os.environ,
            "NXF_ANSI_LOG": "false",
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms1536M -Xmx6144M -XX:ActiveProcessorCount=4",
            "NXF_DISABLE_CHECK_LATEST": "true",
            "NXF_ENABLE_VIRTUAL_THREADS": "false",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    except subprocess.CalledProcessError:
        failed = True
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(
                    urljoins(
                        "latch:///your_log_dir/nf_nf_core_bacass", name, "nextflow.log"
                    )
                )
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)

        print("Computing size of workdir... ", end="")
        try:
            result = subprocess.run(
                ["du", "-sb", str(shared_dir)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5 * 60,
            )

            size = int(result.stdout.split()[0])
            report_nextflow_used_storage(size)
            print(f"Done. Workdir size: {size / 1024 / 1024 / 1024: .2f} GiB")
        except subprocess.TimeoutExpired:
            print(
                "Failed to compute storage size: Operation timed out after 5 minutes."
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to compute storage size: {e.stderr}")
        except Exception as e:
            print(f"Failed to compute storage size: {e}")

    if failed:
        sys.exit(1)
