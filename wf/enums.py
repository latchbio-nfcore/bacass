from enum import Enum


class Assembler(Enum):
    unicycler = "unicycler"
    canu = "canu"
    miniasm = "miniasm"
    dragonflye = "dragonflye"


class AssemblyType(Enum):
    short = "short"
    long = "long"
    hybrid = "hybrid"


class CanuMode(Enum):
    pacbio = "pacbio"
    nanopore = "nanopore"
    pacbio_hifi = "pacbio-hifi"


class PolishMethod(Enum):
    medaka = "medaka"
    nanopolish = "nanopolish"


class AnnotationTool(Enum):
    prokka = "prokka"
    bakta = "bakta"
    dfast = "dfast"


class BaktaDbDownloadArgs(Enum):
    type_light = "--type light"
    type_full = "--type full"
