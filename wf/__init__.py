from pathlib import Path
from typing import List, Optional

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
    input: List[SampleSheet],
    run_name: str,
    email: Optional[str],
    fastp_args: Optional[str],
    save_trimmed: bool,
    save_trimmed_fail: bool,
    save_merged: bool,
    skip_fastqc: bool,
    skip_fastp: bool,
    reference_fasta: Optional[LatchFile],
    reference_gff: Optional[LatchFile],
    unicycler_args: Optional[str],
    canu_mode: Optional[CanuMode],
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
    kraken2db: Optional[LatchFile] = LatchFile(
        "s3://latch-public/nf-core/bacass/databases/k2_standard_8gb_20210517.tar.gz"
    ),
    kmerfinderdb: Optional[LatchFile] = LatchFile(
        "s3://latch-public/nf-core/bacass/databases/20190108_kmerfinder_stable_dirs.tar.gz"
    ),
    ncbi_assembly_metadata: Optional[LatchFile] = LatchFile(
        "s3://latch-public/nf-core/bacass/databases/assembly_summary_refseq.txt"
    ),
    assembler: Assembler = Assembler.unicycler,
    assembly_type: AssemblyType = AssemblyType.short,
    polish_method: PolishMethod = PolishMethod.medaka,
    annotation_tool: AnnotationTool = AnnotationTool.prokka,
    baktadb_download_args: Optional[
        BaktaDbDownloadArgs
    ] = BaktaDbDownloadArgs.type_light,
    dfast_config: Optional[str] = "assets/test_config_dfast.py",
    outdir: LatchOutputDir = LatchOutputDir("latch:///Bacass"),
) -> None:
    """
    nf-core/bacass is a bioinformatics best-practice analysis pipeline for simple bacterial assembly and annotation. The pipeline is able to assemble short reads, long reads, or a mixture of short and long reads (hybrid assembly).

    <html>
    <p align="center">
    <img src="https://user-images.githubusercontent.com/31255434/182289305-4cc620e3-86ae-480f-9b61-6ca83283caa5.jpg" alt="Latch Verified" width="100">
    </p>

    <p align="center">
    <strong>
    Latch Verified
    </strong>
    </p>

    <p align="center">

    [![Cite with Zenodo](http://img.shields.io/badge/DOI-10.5281/zenodo.2669428-1073c8?labelColor=000000)](https://doi.org/10.5281/zenodo.2669428)

    ## Introduction

    **nf-core/bacass** is a bioinformatics best-practice analysis pipeline for simple bacterial assembly and annotation. The pipeline is able to assemble short reads, long reads, or a mixture of short and long reads (hybrid assembly).

    This workflow is hosted on Latch Workflows, using a native Nextflow integration, with a graphical interface for accessible analysis by scientists. There is also an integration with Latch Registry so that batched workflows can be launched from “graphical sample sheets” or tables associating raw sequencing files with metadata.

    The pipeline is built using [Nextflow](https://www.nextflow.io), a workflow tool to run tasks across multiple compute infrastructures in a very portable manner. It uses Docker/Singularity containers making installation trivial and results highly reproducible. The [Nextflow DSL2](https://www.nextflow.io/docs/latest/dsl2.html) implementation of this pipeline uses one container per process which makes it much easier to maintain and update software dependencies.

    ## Pipeline summary

    ### Short Read Assembly

    This pipeline is primarily for bacterial assembly of next-generation sequencing reads. It can be used to quality trim your reads using [FastP](https://github.com/OpenGene/fastp) and performs basic sequencing QC using [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/). Afterwards, the pipeline performs read assembly using [Unicycler](https://github.com/rrwick/Unicycler). Contamination of the assembly is checked using [Kraken2](https://ccb.jhu.edu/software/kraken2/) and [Kmerfinder](https://bitbucket.org/genomicepidemiology/kmerfinder/src/master/) to verify sample purity.

    ### Long Read Assembly

    For users that only have Nanopore data, the pipeline quality trims these using [PoreChop](https://github.com/rrwick/Porechop) and assesses basic sequencing QC utilizing [NanoPlot](https://github.com/wdecoster/NanoPlot) and [PycoQC](https://github.com/a-slide/pycoQC). Contamination of the assembly is checked using [Kraken2](https://ccb.jhu.edu/software/kraken2/) and [Kmerfinder](https://bitbucket.org/genomicepidemiology/kmerfinder/src/master/) to verify sample purity.

    The pipeline can then perform long read assembly utilizing [Unicycler](https://github.com/rrwick/Unicycler), [Miniasm](https://github.com/lh3/miniasm) in combination with [Racon](https://github.com/isovic/racon), [Canu](https://github.com/marbl/canu) or [Flye](https://github.com/fenderglass/Flye) by using the [Dragonflye](https://github.com/rpetit3/dragonflye)(\*) pipeline. Long reads assembly can be polished using [Medaka](https://github.com/nanoporetech/medaka) or [NanoPolish](https://github.com/jts/nanopolish) with Fast5 files.

    > [!NOTE]
    > Dragonflye is a comprehensive pipeline designed for genome assembly of Oxford Nanopore Reads. It facilitates the utilization of Flye (default), Miniasm, and Raven assemblers, along with Racon (default) and Medaka polishers. For more information, visit the [Dragonflye GitHub](https://github.com/rpetit3/dragonflye) repository.

    ### Hybrid Assembly

    For users specifying both short read and long read (NanoPore) data, the pipeline can perform a hybrid assembly approach utilizing [Unicycler](https://github.com/rrwick/Unicycler) (short read assembly followed by gap closing with long reads) or [Dragonflye](https://github.com/rpetit3/dragonflye) (long read assembly followed by polishing with short reads), taking the full set of information from short reads and long reads into account.

    ### Assembly QC and annotation

    In all cases, the assembly is assessed using [QUAST](http://bioinf.spbau.ru/quast). The resulting bacterial assembly is furthermore annotated using [Prokka](https://github.com/tseemann/prokka), [Bakta](https://github.com/oschwengers/bakta) or [DFAST](https://github.com/nigyta/dfast_core).

    If Kmerfinder is invoked, the pipeline will group samples according to the [Kmerfinder](https://bitbucket.org/genomicepidemiology/kmerfinder/src/master/)-estimated reference genomes. Afterwards, two QUAST steps will be carried out: an initial ('general') [QUAST](http://bioinf.spbau.ru/quast) of all samples without reference genomes, and subsequently, a 'by reference genome' [QUAST](http://bioinf.spbau.ru/quast) to aggregate samples with their reference genomes.

    > [!NOTE]
    > This scenario is supported when [Kmerfinder](https://bitbucket.org/genomicepidemiology/kmerfinder/src/master/) analysis is performed only.

    ## Usage

    Prepare a samplesheet with your input data that looks as follows:

    `samplesheet.tsv`:

    ```
    ID      R1                            R2                            LongFastQ                    Fast5    GenomeSize
    shortreads      ./data/S1_R1.fastq.gz       ./data/S1_R2.fastq.gz       NA                            NA      NA
    longreads       NA                          NA                          ./data/S1_long_fastq.gz      ./data/FAST5  2.8m
    shortNlong      ./data/S1_R1.fastq.gz       ./data/S1_R2.fastq.gz       ./data/S1_long_fastq.gz      ./data/FAST5  2.8m

    ```

    Each row represents a fastq file (single-end) or a pair of fastq files (paired end).

    For more details and further functionality, please refer to the [usage documentation](https://nf-co.re/bacass/usage) and the [parameter documentation](https://nf-co.re/bacass/parameters).

    ## Pipeline output

    To see the results of an example test run with a full size dataset refer to the [results](https://nf-co.re/bacass/results) tab on the nf-core website pipeline page.
    For more details about the output files and reports, please refer to the
    [output documentation](https://nf-co.re/bacass/output).

    ## Credits

    nf-core/bacass was initiated by [Andreas Wilm](https://github.com/andreas-wilm), originally written by [Alex Peltzer](https://github.com/apeltzer) (DSL1), rewritten by [Daniel Straub](https://github.com/d4straub) (DSL2) and maintained by [Daniel Valle-Millares](https://github.com/Daniel-VM).

    ## Contributions and Support

    If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

    For further information or help, don't hesitate to get in touch on the [Slack `#bacass` channel](https://nfcore.slack.com/channels/bacass) (you can join with [this invite](https://nf-co.re/join/slack)).

    ## Citations

    If you use nf-core/bacass for your analysis, please cite it using the following doi: [10.5281/zenodo.2669428](https://doi.org/10.5281/zenodo.2669428)

    An extensive list of references for the tools used by the pipeline can be found in the [`CITATIONS.md`](CITATIONS.md) file.

    You can cite the `nf-core` publication as follows:

    > **The nf-core framework for community-curated bioinformatics pipelines.**
    >
    > Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
    >
    > _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

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
                ID="ERR044595",
                R1=LatchFile(
                    "s3://latch-public/nf-core/bacass/test_data/ERR044595_1M_1.fastq.gz"
                ),
                R2=LatchFile(
                    "s3://latch-public/nf-core/bacass/test_data/ERR044595_1M_2.fastq.gz"
                ),
                LongFastQ=None,
                Fast5=None,
                GenomeSize="2.8m",
            ),
            SampleSheet(
                ID="ERR064912",
                R1=LatchFile(
                    "s3://latch-public/nf-core/bacass/test_data/ERR064912_1M_1.fastq.gz"
                ),
                R2=LatchFile(
                    "s3://latch-public/nf-core/bacass/test_data/ERR064912_1M_2.fastq.gz"
                ),
                LongFastQ=None,
                Fast5=None,
                GenomeSize="2.8m",
            ),
        ],
        "run_name": "Test_Run",
        "unicycler_args": "--no_correct --no_pilon",
        "prokka_args": " --fast",
        "assembly_type": AssemblyType.short,
        "skip_pycoqc": True,
        "skip_kraken2": True,
        "skip_kmerfinder": True,
        "dfast_config": "/nf-workdir/assets/test_config_dfast.py",
    },
)
