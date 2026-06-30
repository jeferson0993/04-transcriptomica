process ENRICHMENT {
    tag "${run_id}"
    label 'enrichment'

    input:
    path deg_csv
    val run_id

    output:
    path("go_enrichment.tsv"), emit: go, optional: true
    path("kegg_enrichment.tsv"), emit: kegg, optional: true
    path("gsea_results.tsv"), emit: gsea, optional: true
    path("go_dotplot.png"), emit: go_plot, optional: true
    path("kegg_dotplot.png"), emit: kegg_plot, optional: true
    path("gsea_barplot.png"), emit: gsea_plot, optional: true
    path("gsea_*.png"), emit: gsea_pathways, optional: true

    script:
    """
    Rscript /pipeline/modules/enrichment/enrichment.R \
        --deg ${deg_csv} \
        --organism org.Hs.eg.db \
        --outdir ./
    """
}
