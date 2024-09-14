from pathlib import Path
from typing import Optional

from latch.resources.launch_plan import LaunchPlan
from latch.resources.workflow import workflow
from latch.types import metadata
from latch.types.directory import LatchOutputDir
from latch.types.file import LatchFile
from latch_cli.services.register.utils import import_module_by_path

from wf.entrypoint import (
    AnnotationTool,
    Assembler,
    AssemblyType,
    BaktaDbDownloadArgs,
    CanuMode,
    PolishMethod,
    SampleSheet,
    initialize,
    nextflow_runtime,
)

meta = Path("latch_metadata") / "__init__.py"
import_module_by_path(meta)


@workflow(metadata._nextflow_metadata)
def nf_nf_core_bacass(
    input: str,
    run_name: str,
    email: Optional[str],
    fastp_args: Optional[str],
    save_trimmed: bool,
    save_trimmed_fail: bool,
    save_merged: bool,
    skip_fastqc: bool,
    skip_fastp: bool,
    kraken2db: Optional[str],
    kmerfinderdb: Optional[str],
    reference_fasta: Optional[str],
    reference_gff: Optional[str],
    ncbi_assembly_metadata: Optional[str],
    unicycler_args: Optional[str],
    canu_mode: Optional[str],
    canu_args: Optional[str],
    dragonflye_args: Optional[str],
    prokka_args: Optional[str],
    baktadb: Optional[str],
    baktadb_download: bool,
    skip_kraken2: bool,
    skip_kmerfinder: bool,
    skip_annotation: bool,
    skip_pycoqc: bool,
    skip_polish: bool,
    skip_multiqc: bool,
    multiqc_title: Optional[str],
    multiqc_methods_description: Optional[str],
    assembler: Optional[str] = "unicycler",
    assembly_type: Optional[str] = "short",
    polish_method: Optional[str] = "medaka",
    annotation_tool: Optional[str] = "prokka",
    baktadb_download_args: Optional[str] = "--type light",
    dfast_config: Optional[str] = "assets/test_config_dfast.py",
    outdir: LatchOutputDir = LatchOutputDir("latch:///Bacass"),
) -> None:
    """
    nf-core/bacass

    Sample Description
    """

    pvc_name: str = initialize(run_name=run_name)
    nextflow_runtime(
        run_name=run_name,
        pvc_name=pvc_name,
        input=input,
        outdir=outdir,
        email=email,
        fastp_args=fastp_args,
        save_trimmed=save_trimmed,
        save_trimmed_fail=save_trimmed_fail,
        save_merged=save_merged,
        skip_fastqc=skip_fastqc,
        skip_fastp=skip_fastp,
        kraken2db=kraken2db,
        kmerfinderdb=kmerfinderdb,
        reference_fasta=reference_fasta,
        reference_gff=reference_gff,
        ncbi_assembly_metadata=ncbi_assembly_metadata,
        assembler=assembler,
        assembly_type=assembly_type,
        unicycler_args=unicycler_args,
        canu_mode=canu_mode,
        canu_args=canu_args,
        dragonflye_args=dragonflye_args,
        polish_method=polish_method,
        annotation_tool=annotation_tool,
        prokka_args=prokka_args,
        baktadb=baktadb,
        baktadb_download=baktadb_download,
        baktadb_download_args=baktadb_download_args,
        dfast_config=dfast_config,
        skip_kraken2=skip_kraken2,
        skip_kmerfinder=skip_kmerfinder,
        skip_annotation=skip_annotation,
        skip_pycoqc=skip_pycoqc,
        skip_polish=skip_polish,
        skip_multiqc=skip_multiqc,
        multiqc_title=multiqc_title,
        multiqc_methods_description=multiqc_methods_description,
    )


LaunchPlan(
    nf_nf_core_bacass,
    "Short Assembly with Fast Annotation",
    {
        "input": [
            SampleSheet(
                sample="test_sample_1",
                fastq_1=LatchFile("latch:///path/to/test_sample_1_R1.fastq.gz"),
                fastq_2=LatchFile("latch:///path/to/test_sample_1_R2.fastq.gz"),
            ),
            SampleSheet(
                sample="test_sample_2",
                fastq_1=LatchFile("latch:///path/to/test_sample_2_R1.fastq.gz"),
                fastq_2=LatchFile("latch:///path/to/test_sample_2_R2.fastq.gz"),
            ),
        ],
        "run_name": "test_short_assembly",
        "outdir": LatchFile("latch:///bacterial_genomics_output"),
        "unicycler_args": "--no_correct --no_pilon",
        "prokka_args": "--fast",
        "assembly_type": "short",
        "skip_pycoqc": True,
        "skip_kraken2": True,
        "skip_kmerfinder": True,
    },
)
