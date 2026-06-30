#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(rmarkdown)
    library(knitr)
    library(DT)
    library(plotly)
})

args <- commandArgs(trailingOnly = TRUE)

template <- sub("--template=", "", args[grep("--template", args)])
outdir <- sub("--outdir=", "", args[grep("--outdir", args)])
run_id <- sub("--run_id=", "", args[grep("--run_id", args)])
design_formula <- sub("--design=", "", args[grep("--design", args)])
norm_path <- sub("--norm=", "", args[grep("--norm", args)])
deg_path <- sub("--deg=", "", args[grep("--deg", args)])
pca_path <- sub("--pca=", "", args[grep("--pca", args)])
volcano_path <- sub("--volcano=", "", args[grep("--volcano", args)])
ma_path <- sub("--ma=", "", args[grep("--ma", args)])
heatmap_path <- sub("--heatmap=", "", args[grep("--heatmap", args)])
correlation_path <- sub("--correlation=", "", args[grep("--correlation", args)])
go_path <- sub("--go=", "", args[grep("--go", args)])
kegg_path <- sub("--kegg=", "", args[grep("--kegg", args)])
gsea_path <- sub("--gsea=", "", args[grep("--gsea", args)])

if (length(outdir) == 0 || outdir == "") outdir <- "./"
if (length(template) == 0 || template == "") template <- "/pipeline/modules/deseq2/report_enhanced.Rmd"

render(
    input = template,
    output_file = "deseq2_report.html",
    output_dir = outdir,
    params = list(
        run_id = run_id,
        design_formula = design_formula,
        norm_counts_path = norm_path,
        deg_results_path = deg_path,
        pca_plot_path = pca_path,
        volcano_plot_path = volcano_path,
        ma_plot_path = ma_path,
        heatmap_path = heatmap_path,
        correlation_path = correlation_path,
        go_path = go_path,
        kegg_path = kegg_path,
        gsea_path = gsea_path
    ),
    intermediates_dir = outdir,
    knit_root_dir = outdir,
    quiet = TRUE
)

cat(sprintf("Enhanced report rendered: %s/deseq2_report.html\n", outdir))
