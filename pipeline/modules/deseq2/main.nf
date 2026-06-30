process DESEQ2 {
    tag "${run_id}"
    label 'deseq2'

    input:
    path count_matrix
    path samplesheet
    val design_formula
    val run_id

    output:
    path("normalized_counts.csv"), emit: norm_counts
    path("deg_results.csv"), emit: deg_results
    path("pca_plot.png"), emit: pca_plot, optional: true
    path("volcano_plot.png"), emit: volcano_plot, optional: true
    path("ma_plot.png"), emit: ma_plot, optional: true
    path("heatmap.png"), emit: heatmap, optional: true
    path("sample_correlation.png"), emit: correlation, optional: true
    path("gene_coverage.png"), emit: coverage, optional: true
    path("batch_pca.png"), emit: batch_pca, optional: true
    path("pca_variance.png"), emit: pca_var, optional: true
    path("deseq2_report.html"), emit: report, optional: true

    script:
    """
    Rscript /pipeline/modules/deseq2/qc_advanced.R \
        --count_matrix ${count_matrix} \
        --samplesheet ${samplesheet} \
        --outdir ./

    Rscript /pipeline/modules/deseq2/deseq2.R \
        --count_matrix ${count_matrix} \
        --samplesheet ${samplesheet} \
        --design_formula "${design_formula}" \
        --run_id ${run_id} \
        --outdir ./

    Rscript /pipeline/modules/deseq2/render_report.R \
        --template /pipeline/modules/deseq2/report_enhanced.Rmd \
        --run_id ${run_id} \
        --design "${design_formula}" \
        --norm ./normalized_counts.csv \
        --deg ./deg_results.csv \
        --pca ./pca_plot.png \
        --volcano ./volcano_plot.png \
        --ma ./ma_plot.png \
        --heatmap ./heatmap.png \
        --correlation ./sample_correlation.png \
        --outdir ./
    """
}
