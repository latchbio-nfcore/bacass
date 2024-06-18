
from dataclasses import dataclass
import typing
import typing_extensions

from flytekit.core.annotation import FlyteAnnotation

from latch.types.metadata import NextflowParameter
from latch.types.file import LatchFile
from latch.types.directory import LatchDir, LatchOutputDir

# Import these into your `__init__.py` file:
#
# from .parameters import generated_parameters

generated_parameters = {
    'input': NextflowParameter(
        type=str,
        default=None,
        section_title='Input/output options',
        description='Path to tab-separated sample sheet',
    ),
    'outdir': NextflowParameter(
        type=typing_extensions.Annotated[LatchDir, FlyteAnnotation({'output': True})],
        default=None,
        section_title=None,
        description='The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure.',
    ),
    'email': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Email address for completion summary.',
    ),
    'fastp_args': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='QC and Trim',
        description='This can be used to pass arguments to [Fastp](https://github.com/OpenGene/fastp)',
    ),
    'save_trimmed': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='save trimmed files',
    ),
    'save_trimmed_fail': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='save files that failed to pass trimming thresholds ending in `*.fail.fastq.gz`',
    ),
    'save_merged': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='save all merged reads to the a file ending in `*.merged.fastq.gz`',
    ),
    'skip_fastqc': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip FastQC',
    ),
    'skip_fastp': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip FastP',
    ),
    'kraken2db': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Contamination Screening',
        description='Path to Kraken2 database.',
    ),
    'kmerfinderdb': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to the Kmerfinder bacteria database. For more details, see [Kmerfinder Databases](https://bitbucket.org/genomicepidemiology/kmerfinder_db/src/master/). You can also download precomputed Kmerfinder database (dated 2019/01/08) from https://zenodo.org/records/10458361/files/20190108_kmerfinder_stable_dirs.tar.gz ',
    ),
    'reference_fasta': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Reference FASTA file.',
    ),
    'reference_gff': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Reference GFF file.',
    ),
    'ncbi_assembly_metadata': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Master file (*.txt) containing a summary of assemblies available in GeneBank or RefSeq. See: https://ftp.ncbi.nlm.nih.gov/genomes/README_assembly_summary.txt',
    ),
    'assembler': NextflowParameter(
        type=typing.Optional[str],
        default='unicycler',
        section_title='Assembly parameters',
        description='The assembler to use for assembly. Use the appropriate assembler according to the chosen assembly_type. Refer to the README.md for further clarification.',
    ),
    'assembly_type': NextflowParameter(
        type=typing.Optional[str],
        default='short',
        section_title=None,
        description='Which type of assembly to perform.',
    ),
    'unicycler_args': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Extra arguments for Unicycler',
    ),
    'canu_mode': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Allowed technologies for long read assembly.',
    ),
    'canu_args': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='This can be used to supply [extra options](https://canu.readthedocs.io/en/latest/quick-start.html) to the Canu assembler. Will be ignored when other assemblers are used.',
    ),
    'dragonflye_args': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Extra arguments for [Dragonflye](https://github.com/rpetit3/dragonflye#usage)',
    ),
    'polish_method': NextflowParameter(
        type=typing.Optional[str],
        default='medaka',
        section_title='Assembly Polishing',
        description='Which assembly polishing method to use.',
    ),
    'annotation_tool': NextflowParameter(
        type=typing.Optional[str],
        default='prokka',
        section_title='Annotation',
        description='The annotation method to annotate the final assembly.',
    ),
    'prokka_args': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Extra arguments for prokka annotation tool.',
    ),
    'baktadb': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Path to Bakta database',
    ),
    'baktadb_download': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Download Bakta database',
    ),
    'baktadb_download_args': NextflowParameter(
        type=typing.Optional[str],
        default='--type light',
        section_title=None,
        description='This can be used to supply [extra options](https://github.com/oschwengers/bakta#database-download) to the Bakta download module',
    ),
    'dfast_config': NextflowParameter(
        type=typing.Optional[str],
        default='assets/test_config_dfast.py',
        section_title=None,
        description='Specifies a configuration file for the [DFAST](https://github.com/nigyta/dfast_core) annotation method.',
    ),
    'skip_kraken2': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title='Skipping Options',
        description='Skip running Kraken2 classifier on reads.',
    ),
    'skip_kmerfinder': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip contamination analysis with [Kmerfinder](https://bitbucket.org/genomicepidemiology/kmerfinder/src/master/)',
    ),
    'skip_annotation': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip annotating the assembly with Prokka /DFAST.',
    ),
    'skip_pycoqc': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip running `PycoQC` on long read input.',
    ),
    'skip_polish': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip polishing the long-read assembly with fast5 input. Will not affect short/hybrid assemblies.',
    ),
    'skip_multiqc': NextflowParameter(
        type=typing.Optional[bool],
        default=None,
        section_title=None,
        description='Skip MultiQC',
    ),
    'multiqc_title': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title='Generic options',
        description='MultiQC report title. Printed as page header, used for filename if not otherwise specified.',
    ),
    'multiqc_methods_description': NextflowParameter(
        type=typing.Optional[str],
        default=None,
        section_title=None,
        description='Custom MultiQC yaml file containing HTML including a methods description.',
    ),
}

