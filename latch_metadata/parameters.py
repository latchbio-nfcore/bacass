import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import (
    LatchRule,
    NextflowParameter,
    Params,
    Section,
    Spoiler,
    Text,
)


@dataclass(frozen=True)
class SampleSheet:
    ID: str
    R1: LatchFile
    R2: LatchFile
    LongFastQ: Optional[LatchFile]
    Fast5: Optional[LatchDir]
    GenomeSize: Optional[str]


def custom_samplesheet_constructor(
    samples: List[SampleSheet], shared_dir: Path
) -> Path:
    samplesheet = Path(shared_dir / "samplesheet.tsv")
    columns = ["ID", "R1", "R2", "LongFastQ", "Fast5", "GenomeSize"]

    with open(samplesheet, "w") as f:
        writer = csv.DictWriter(f, columns, delimiter="\t")
        writer.writeheader()

        for sample in samples:
            row_data = {
                "ID": sample.ID,
                "R1": str(sample.R1.remote_path),
                "R2": str(sample.R2.remote_path),
                "LongFastQ": str(sample.LongFastQ.remote_path)
                if sample.LongFastQ
                else "NA",
                "Fast5": str(sample.Fast5.remote_path) if sample.Fast5 else "NA",
                "GenomeSize": str(sample.GenomeSize) if sample.GenomeSize else "NA",
            }
            writer.writerow(row_data)

    return samplesheet


flow = [
    Section(
        "Input",
        Params(
            "input",
        ),
    ),
    Section(
        "Assembly",
        Params(
            "assembler",
            "polish_method",
            "assembly_type",
        ),
        Spoiler(
            "Advanced Assembly Options",
            Params(
                "canu_mode",
                "unicycler_args",
                "canu_args",
                "dragonflye_args",
            ),
        ),
    ),
    Section(
        "Annotation",
        Params("annotation_tool"),
        Spoiler(
            "Advanced Annotation Options",
            Params(
                "prokka_args",
                "baktadb",
                "baktadb_download",
                "baktadb_download_args",
                "dfast_config",
            ),
        ),
    ),
    Section(
        "Output Directory",
        Params("run_name"),
        Text("Parent directory for outputs"),
        Params("outdir"),
    ),
    Spoiler(
        "Advanced Options",
        Spoiler(
            "QC and Trim",
            Params(
                "fastp_args",
                "save_trimmed",
                "save_trimmed_fail",
                "save_merged",
                "skip_fastqc",
                "skip_fastp",
            ),
        ),
        Spoiler(
            "Contamination Screening and References",
            Params(
                "kraken2db",
                "kmerfinderdb",
                "reference_fasta",
                "reference_gff",
                "ncbi_assembly_metadata",
            ),
        ),
        Spoiler(
            "Skipping Steps",
            Params(
                "skip_kraken2",
                "skip_kmerfinder",
                "skip_annotation",
                "skip_pycoqc",
                "skip_polish",
                "skip_multiqc",
            ),
        ),
        Spoiler(
            "MultiQC Options",
            Params(
                "email",
                "multiqc_title",
                "multiqc_methods_description",
            ),
        ),
    ),
]


generated_parameters = {
    "input": NextflowParameter(
        type=List[SampleSheet],
        display_name="Sample Sheet",
        samplesheet=True,
        samplesheet_constructor=custom_samplesheet_constructor,
    ),
    "run_name": NextflowParameter(
        type=str,
        display_name="Run Name",
        description="Name of run",
        batch_table_column=True,
        rules=[
            LatchRule(
                regex=r"^[a-zA-Z0-9_-]+$",
                message="Run name must contain only letters, digits, underscores, and dashes. No spaces are allowed.",
            )
        ],
    ),
    "outdir": NextflowParameter(
        type=LatchOutputDir,
        display_name="Output Directory",
        default=None,
        section_title=None,
        description="The output directory where the results will be saved.",
    ),
    "email": NextflowParameter(
        type=Optional[str],
        display_name="Email Address",
        default=None,
        section_title=None,
        description="Email address for completion summary.",
    ),
    "fastp_args": NextflowParameter(
        type=Optional[str],
        display_name="Fastp Arguments",
        default=None,
        description="This can be used to pass arguments to [Fastp](https://github.com/OpenGene/fastp)",
    ),
    "save_trimmed": NextflowParameter(
        type=bool,
        display_name="Save Trimmed Files",
        default=None,
        section_title=None,
        description="save trimmed files",
    ),
    "save_trimmed_fail": NextflowParameter(
        type=bool,
        display_name="Save Failed Trimmed Files",
        default=None,
        section_title=None,
        description="save files that failed to pass trimming thresholds ending in `*.fail.fastq.gz`",
    ),
    "save_merged": NextflowParameter(
        type=bool,
        display_name="Save Merged Reads",
        default=None,
        section_title=None,
        description="save all merged reads to the a file ending in `*.merged.fastq.gz`",
    ),
    "skip_fastqc": NextflowParameter(
        type=bool,
        display_name="Skip FastQC",
        default=None,
        section_title=None,
        description="Skip FastQC",
    ),
    "skip_fastp": NextflowParameter(
        type=bool,
        display_name="Skip Fastp",
        default=None,
        section_title=None,
        description="Skip FastP",
    ),
    "kraken2db": NextflowParameter(
        type=Optional[str],
        display_name="Kraken2 Database",
        default=None,
        description="Path to Kraken2 database.",
    ),
    "kmerfinderdb": NextflowParameter(
        type=Optional[str],
        display_name="Kmerfinder Database",
        default=None,
        section_title=None,
        description="Path to the Kmerfinder bacteria database. For more details, see [Kmerfinder Databases](https://bitbucket.org/genomicepidemiology/kmerfinder_db/src/master/). You can also download precomputed Kmerfinder database (dated 2019/01/08) from https://zenodo.org/records/10458361/files/20190108_kmerfinder_stable_dirs.tar.gz ",
    ),
    "reference_fasta": NextflowParameter(
        type=Optional[str],
        display_name="Reference FASTA",
        default=None,
        section_title=None,
        description="Reference FASTA file.",
    ),
    "reference_gff": NextflowParameter(
        type=Optional[str],
        display_name="Reference GFF",
        default=None,
        section_title=None,
        description="Reference GFF file.",
    ),
    "ncbi_assembly_metadata": NextflowParameter(
        type=Optional[str],
        display_name="NCBI Assembly Metadata",
        default=None,
        section_title=None,
        description="Master file (*.txt) containing a summary of assemblies available in GeneBank or RefSeq. See: https://ftp.ncbi.nlm.nih.gov/genomes/README_assembly_summary.txt",
    ),
    "assembler": NextflowParameter(
        type=Optional[str],
        display_name="Assembler",
        default="unicycler",
        description="The assembler to use for assembly. Use the appropriate assembler according to the chosen assembly_type. Refer to the README.md for further clarification.",
    ),
    "assembly_type": NextflowParameter(
        type=Optional[str],
        display_name="Assembly Type",
        default="short",
        section_title=None,
        description="Which type of assembly to perform.",
    ),
    "unicycler_args": NextflowParameter(
        type=Optional[str],
        display_name="Unicycler Arguments",
        default=None,
        section_title=None,
        description="Extra arguments for Unicycler",
    ),
    "canu_mode": NextflowParameter(
        type=Optional[str],
        display_name="Canu Mode",
        default=None,
        section_title=None,
        description="Allowed technologies for long read assembly.",
    ),
    "canu_args": NextflowParameter(
        type=Optional[str],
        display_name="Canu Arguments",
        default=None,
        section_title=None,
        description="This can be used to supply [extra options](https://canu.readthedocs.io/en/latest/quick-start.html) to the Canu assembler. Will be ignored when other assemblers are used.",
    ),
    "dragonflye_args": NextflowParameter(
        type=Optional[str],
        display_name="Dragonflye Arguments",
        default=None,
        section_title=None,
        description="Extra arguments for [Dragonflye](https://github.com/rpetit3/dragonflye#usage)",
    ),
    "polish_method": NextflowParameter(
        type=Optional[str],
        display_name="Polish Method",
        default="medaka",
        description="Which assembly polishing method to use.",
    ),
    "annotation_tool": NextflowParameter(
        type=Optional[str],
        display_name="Annotation Tool",
        default="prokka",
        description="The annotation method to annotate the final assembly.",
    ),
    "prokka_args": NextflowParameter(
        type=Optional[str],
        display_name="Prokka Arguments",
        default=None,
        section_title=None,
        description="Extra arguments for prokka annotation tool.",
    ),
    "baktadb": NextflowParameter(
        type=Optional[str],
        display_name="Bakta Database",
        default=None,
        section_title=None,
        description="Path to Bakta database",
    ),
    "baktadb_download": NextflowParameter(
        type=bool,
        display_name="Download Bakta Database",
        default=None,
        section_title=None,
        description="Download Bakta database",
    ),
    "baktadb_download_args": NextflowParameter(
        type=Optional[str],
        display_name="Bakta Download Arguments",
        default="--type light",
        section_title=None,
        description="This can be used to supply [extra options](https://github.com/oschwengers/bakta#database-download) to the Bakta download module",
    ),
    "dfast_config": NextflowParameter(
        type=Optional[str],
        display_name="DFAST Config",
        default="assets/test_config_dfast.py",
        section_title=None,
        description="Specifies a configuration file for the [DFAST](https://github.com/nigyta/dfast_core) annotation method.",
    ),
    "skip_kraken2": NextflowParameter(
        type=bool,
        display_name="Skip Kraken2",
        default=None,
        description="Skip running Kraken2 classifier on reads.",
    ),
    "skip_kmerfinder": NextflowParameter(
        type=bool,
        display_name="Skip Kmerfinder",
        default=None,
        section_title=None,
        description="Skip contamination analysis with [Kmerfinder](https://bitbucket.org/genomicepidemiology/kmerfinder/src/master/)",
    ),
    "skip_annotation": NextflowParameter(
        type=bool,
        display_name="Skip Annotation",
        default=None,
        section_title=None,
        description="Skip annotating the assembly with Prokka /DFAST.",
    ),
    "skip_pycoqc": NextflowParameter(
        type=bool,
        display_name="Skip PycoQC",
        default=None,
        section_title=None,
        description="Skip running `PycoQC` on long read input.",
    ),
    "skip_polish": NextflowParameter(
        type=bool,
        display_name="Skip Polish",
        default=None,
        section_title=None,
        description="Skip polishing the long-read assembly with fast5 input. Will not affect short/hybrid assemblies.",
    ),
    "skip_multiqc": NextflowParameter(
        type=bool,
        display_name="Skip MultiQC",
        default=None,
        section_title=None,
        description="Skip MultiQC",
    ),
    "multiqc_title": NextflowParameter(
        type=Optional[str],
        display_name="MultiQC Title",
        default=None,
        description="MultiQC report title. Printed as page header, used for filename if not otherwise specified.",
    ),
    "multiqc_methods_description": NextflowParameter(
        type=Optional[str],
        display_name="MultiQC Methods Description",
        default=None,
        section_title=None,
        description="Custom MultiQC yaml file containing HTML including a methods description.",
    ),
}
