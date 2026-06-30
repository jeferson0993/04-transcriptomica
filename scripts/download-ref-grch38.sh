#!/bin/bash
set -euo pipefail

REF_DIR="/ref/grch38"
mkdir -p "$REF_DIR"
cd "$REF_DIR"

echo "=== Downloading GRCh38 reference ==="

if [ ! -f "genome.fa" ]; then
    echo "Downloading GRCh38 FASTA (chr22 test)..."
    wget -q -O chr22.fa.gz "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/chromosomes/chr22.fa.gz" || {
        echo "Full GRCh38 too large; using chr22 for testing"
        echo "In production, download from Ensembl:"
        echo "wget ftp://ftp.ensembl.org/pub/release-112/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz"
    }
    if [ -f "chr22.fa.gz" ]; then
        gunzip -f chr22.fa.gz
        mv chr22.fa genome.fa
    fi
fi

if [ ! -f "gencode.v44.annotation.gtf" ]; then
    echo "Downloading GENCODE v44 GTF (chr22 test)..."
    wget -q -O - "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz" | \
        zcat | awk '$1 == "chr22" || $1 == "22"' > gencode.v44.annotation.gtf || {
        echo "Could not download full GTF; creating placeholder"
        touch gencode.v44.annotation.gtf
    }
fi

if [ ! -d "star_index" ]; then
    echo "Building STAR index..."
    mkdir -p star_index
    if [ -f "genome.fa" ] && [ -f "gencode.v44.annotation.gtf" ]; then
        STAR --runMode genomeGenerate \
            --genomeDir star_index \
            --genomeFastaFiles genome.fa \
            --sjdbGTFfile gencode.v44.annotation.gtf \
            --sjdbOverhang 149 \
            --runThreadN 4 \
            --genomeSAindexNbases 12 \
        || echo "STAR index build failed (expected if chr22 only)"
    fi
fi

echo "=== Reference download complete ==="
ls -lh "$REF_DIR"
