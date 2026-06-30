#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

includeConfig "${projectDir}/conf/base.config"
includeConfig "${projectDir}/conf/docker.config"

if (params.test_mode) {
    includeConfig "${projectDir}/conf/test.config"
}
if (params.reference == "grch38_gencode_v44") {
    includeConfig "${projectDir}/conf/grch38.config"
}

include { FASTQC } from "${projectDir}/modules/nf-core/fastqc.nf"
include { DESEQ2 } from "${projectDir}/modules/deseq2/main.nf"
include { ENRICHMENT } from "${projectDir}/modules/enrichment/main.nf"
include { MULTIQC } from "${projectDir}/modules/nf-core/multiqc.nf"

params.samplesheet = "${projectDir}/assets/samplesheet.csv"
params.reference = "grch38_gencode_v44"
params.design_formula = "~condition"
params.outdir = "./results"
params.run_id = "run_001"
params.test_mode = false
params.star_extra_args = ""

samplesheet_ch = Channel.fromPath(params.samplesheet)
    .splitCsv(header: true, sep: ',')
    .map { row ->
        [row.sample, file(row.fastq_1), file(row.fastq_2), row.condition, row.batch]
    }

workflow {
    fastqc_raw_ch = FASTQC(samplesheet_ch.map { it[0..2] })

    trimmed_ch = TRIMMING(samplesheet_ch)

    fastqc_trimmed_ch = FASTQC(trimmed_ch.map { it[0..2] })

    aligned_ch = STAR_ALIGN(trimmed_ch, params.star_extra_args)

    count_matrix_ch = FEATURECOUNTS(aligned_ch)

    multiqc_report = MULTIQC(fastqc_raw_ch.mix(fastqc_trimmed_ch, aligned_ch.map { it[1] }))

    samplesheet_file = file(params.samplesheet)

    deseq2_results = DESEQ2(
        count_matrix_ch,
        samplesheet_file,
        params.design_formula,
        params.run_id
    )

    enrichment_results = ENRICHMENT(
        deseq2_results.deg_results,
        params.run_id
    )

    deseq2_results.report | view { "DESeq2 report: ${it}" }
    enrichment_results.go_plot | view { "GO enrichment plot: ${it}" }
}

workflow.onComplete {
    def run_id = params.run_id
    def outdir = file(params.outdir)
    outdir.mkdirs()

    multiqc_report.subscribe { report ->
        copyTo(report, "${outdir}/multiqc_report.html")
    }

    deseq2_results.subscribe { results ->
        results.each { name, file_obj ->
            copyTo(file_obj, "${outdir}/${name}")
        }
    }

    if (workflow.success) {
        log.info "Pipeline completed successfully for run ${run_id}"
        file(".exitcode").text = "0"
    } else {
        log.error "Pipeline failed for run ${run_id}"
        file(".exitcode").text = "1"
    }
    workflow.cleanup = true
}
