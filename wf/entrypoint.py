from dataclasses import dataclass
from enum import Enum
import os
import subprocess
import requests
import shutil
from pathlib import Path
import typing
import typing_extensions

from latch.resources.workflow import workflow
from latch.resources.tasks import nextflow_runtime_task, custom_task
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir
from latch.ldata.path import LPath
from latch_cli.nextflow.workflow import get_flag
from latch_cli.nextflow.utils import _get_execution_name
from latch_cli.utils import urljoins
from latch.types import metadata
from flytekit.core.annotation import FlyteAnnotation

from latch_cli.services.register.utils import import_module_by_path

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)
import latch_metadata

@custom_task(cpu=0.25, memory=0.5, storage_gib=1)
def initialize() -> str:
    token = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID")
    if token is None:
        raise RuntimeError("failed to get execution token")

    headers = {"Authorization": f"Latch-Execution-Token {token}"}

    print("Provisioning shared storage volume... ", end="")
    resp = requests.post(
        "http://nf-dispatcher-service.flyte.svc.cluster.local/provision-storage",
        headers=headers,
        json={
            "storage_gib": 100,
        }
    )
    resp.raise_for_status()
    print("Done.")

    return resp.json()["name"]






@nextflow_runtime_task(cpu=4, memory=8, storage_gib=100)
def nextflow_runtime(pvc_name: str, input: str, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], fastp_args: typing.Optional[str], save_trimmed: typing.Optional[bool], save_trimmed_fail: typing.Optional[bool], save_merged: typing.Optional[bool], skip_fastqc: typing.Optional[bool], skip_fastp: typing.Optional[bool], kraken2db: typing.Optional[str], kmerfinderdb: typing.Optional[str], reference_fasta: typing.Optional[str], reference_gff: typing.Optional[str], ncbi_assembly_metadata: typing.Optional[str], unicycler_args: typing.Optional[str], canu_mode: typing.Optional[str], canu_args: typing.Optional[str], dragonflye_args: typing.Optional[str], prokka_args: typing.Optional[str], baktadb: typing.Optional[str], baktadb_download: typing.Optional[bool], skip_kraken2: typing.Optional[bool], skip_kmerfinder: typing.Optional[bool], skip_annotation: typing.Optional[bool], skip_pycoqc: typing.Optional[bool], skip_polish: typing.Optional[bool], skip_multiqc: typing.Optional[bool], multiqc_title: typing.Optional[str], multiqc_methods_description: typing.Optional[str], assembler: typing.Optional[str], assembly_type: typing.Optional[str], polish_method: typing.Optional[str], annotation_tool: typing.Optional[str], baktadb_download_args: typing.Optional[str], dfast_config: typing.Optional[str]) -> None:
    try:
        shared_dir = Path("/nf-workdir")



        ignore_list = [
            "latch",
            ".latch",
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
                *get_flag('input', input),
                *get_flag('outdir', outdir),
                *get_flag('email', email),
                *get_flag('fastp_args', fastp_args),
                *get_flag('save_trimmed', save_trimmed),
                *get_flag('save_trimmed_fail', save_trimmed_fail),
                *get_flag('save_merged', save_merged),
                *get_flag('skip_fastqc', skip_fastqc),
                *get_flag('skip_fastp', skip_fastp),
                *get_flag('kraken2db', kraken2db),
                *get_flag('kmerfinderdb', kmerfinderdb),
                *get_flag('reference_fasta', reference_fasta),
                *get_flag('reference_gff', reference_gff),
                *get_flag('ncbi_assembly_metadata', ncbi_assembly_metadata),
                *get_flag('assembler', assembler),
                *get_flag('assembly_type', assembly_type),
                *get_flag('unicycler_args', unicycler_args),
                *get_flag('canu_mode', canu_mode),
                *get_flag('canu_args', canu_args),
                *get_flag('dragonflye_args', dragonflye_args),
                *get_flag('polish_method', polish_method),
                *get_flag('annotation_tool', annotation_tool),
                *get_flag('prokka_args', prokka_args),
                *get_flag('baktadb', baktadb),
                *get_flag('baktadb_download', baktadb_download),
                *get_flag('baktadb_download_args', baktadb_download_args),
                *get_flag('dfast_config', dfast_config),
                *get_flag('skip_kraken2', skip_kraken2),
                *get_flag('skip_kmerfinder', skip_kmerfinder),
                *get_flag('skip_annotation', skip_annotation),
                *get_flag('skip_pycoqc', skip_pycoqc),
                *get_flag('skip_polish', skip_polish),
                *get_flag('skip_multiqc', skip_multiqc),
                *get_flag('multiqc_title', multiqc_title),
                *get_flag('multiqc_methods_description', multiqc_methods_description)
        ]

        print("Launching Nextflow Runtime")
        print(' '.join(cmd))
        print(flush=True)

        env = {
            **os.environ,
            "NXF_HOME": "/root/.nextflow",
            "NXF_OPTS": "-Xms2048M -Xmx8G -XX:ActiveProcessorCount=4",
            "K8S_STORAGE_CLAIM_NAME": pvc_name,
            "NXF_DISABLE_CHECK_LATEST": "true",
        }
        subprocess.run(
            cmd,
            env=env,
            check=True,
            cwd=str(shared_dir),
        )
    finally:
        print()

        nextflow_log = shared_dir / ".nextflow.log"
        if nextflow_log.exists():
            name = _get_execution_name()
            if name is None:
                print("Skipping logs upload, failed to get execution name")
            else:
                remote = LPath(urljoins("latch:///your_log_dir/nf_nf_core_bacass", name, "nextflow.log"))
                print(f"Uploading .nextflow.log to {remote.path}")
                remote.upload_from(nextflow_log)



@workflow(metadata._nextflow_metadata)
def nf_nf_core_bacass(input: str, outdir: typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})], email: typing.Optional[str], fastp_args: typing.Optional[str], save_trimmed: typing.Optional[bool], save_trimmed_fail: typing.Optional[bool], save_merged: typing.Optional[bool], skip_fastqc: typing.Optional[bool], skip_fastp: typing.Optional[bool], kraken2db: typing.Optional[str], kmerfinderdb: typing.Optional[str], reference_fasta: typing.Optional[str], reference_gff: typing.Optional[str], ncbi_assembly_metadata: typing.Optional[str], unicycler_args: typing.Optional[str], canu_mode: typing.Optional[str], canu_args: typing.Optional[str], dragonflye_args: typing.Optional[str], prokka_args: typing.Optional[str], baktadb: typing.Optional[str], baktadb_download: typing.Optional[bool], skip_kraken2: typing.Optional[bool], skip_kmerfinder: typing.Optional[bool], skip_annotation: typing.Optional[bool], skip_pycoqc: typing.Optional[bool], skip_polish: typing.Optional[bool], skip_multiqc: typing.Optional[bool], multiqc_title: typing.Optional[str], multiqc_methods_description: typing.Optional[str], assembler: typing.Optional[str] = 'unicycler', assembly_type: typing.Optional[str] = 'short', polish_method: typing.Optional[str] = 'medaka', annotation_tool: typing.Optional[str] = 'prokka', baktadb_download_args: typing.Optional[str] = '--type light', dfast_config: typing.Optional[str] = 'assets/test_config_dfast.py') -> None:
    """
    nf-core/bacass

    Sample Description
    """

    pvc_name: str = initialize()
    nextflow_runtime(pvc_name=pvc_name, input=input, outdir=outdir, email=email, fastp_args=fastp_args, save_trimmed=save_trimmed, save_trimmed_fail=save_trimmed_fail, save_merged=save_merged, skip_fastqc=skip_fastqc, skip_fastp=skip_fastp, kraken2db=kraken2db, kmerfinderdb=kmerfinderdb, reference_fasta=reference_fasta, reference_gff=reference_gff, ncbi_assembly_metadata=ncbi_assembly_metadata, assembler=assembler, assembly_type=assembly_type, unicycler_args=unicycler_args, canu_mode=canu_mode, canu_args=canu_args, dragonflye_args=dragonflye_args, polish_method=polish_method, annotation_tool=annotation_tool, prokka_args=prokka_args, baktadb=baktadb, baktadb_download=baktadb_download, baktadb_download_args=baktadb_download_args, dfast_config=dfast_config, skip_kraken2=skip_kraken2, skip_kmerfinder=skip_kmerfinder, skip_annotation=skip_annotation, skip_pycoqc=skip_pycoqc, skip_polish=skip_polish, skip_multiqc=skip_multiqc, multiqc_title=multiqc_title, multiqc_methods_description=multiqc_methods_description)

