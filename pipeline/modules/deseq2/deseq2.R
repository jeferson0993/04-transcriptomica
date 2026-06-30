#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(DESeq2)
    library(EnhancedVolcano)
    library(pheatmap)
    library(ggplot2)
})

args <- commandArgs(trailingOnly = TRUE)

count_matrix_path <- sub("--count_matrix=", "", args[grep("--count_matrix", args)])
samplesheet_path <- sub("--samplesheet=", "", args[grep("--samplesheet", args)])
design_formula_str <- sub("--design_formula=", "", args[grep("--design_formula", args)])
run_id <- sub("--run_id=", "", args[grep("--run_id", args)])
outdir <- sub("--outdir=", "", args[grep("--outdir", args)])

if (length(outdir) == 0 || outdir == "") outdir <- "./"

set.seed(42)

count_data <- read.csv(count_matrix_path, row.names = 1, check.names = FALSE)

if (file.exists(samplesheet_path)) {
    samplesheet <- read.csv(samplesheet_path, row.names = 1, check.names = FALSE)
    common <- intersect(colnames(count_data), rownames(samplesheet))
    count_data <- count_data[, common, drop = FALSE]
    samplesheet <- samplesheet[common, , drop = FALSE]
    col_data <- samplesheet
} else {
    col_data <- data.frame(
        sample = colnames(count_data),
        condition = factor(gsub("_.*", "", colnames(count_data))),
        batch = factor(rep("batch1", ncol(count_data)))
    )
    rownames(col_data) <- col_data$sample
    col_data$sample <- NULL
}

for (col in colnames(col_data)) {
    if (is.character(col_data[[col]])) {
        col_data[[col]] <- factor(col_data[[col]])
    }
}

design_formula <- as.formula(design_formula_str)

dds <- DESeqDataSetFromMatrix(
    countData = count_data,
    colData = col_data,
    design = design_formula
)

dds <- DESeq(dds)

norm_counts <- counts(dds, normalized = TRUE)
write.csv(norm_counts, file.path(outdir, "normalized_counts.csv"))

results_names <- resultsNames(dds)
for (res_name in results_names[grep("condition", results_names)]) {
    res <- results(dds, name = res_name)
    res_df <- as.data.frame(res)
    res_df$gene <- rownames(res_df)
    res_df <- res_df[, c("gene", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj")]
    res_df <- res_df[order(res_df$padj), ]
    write.csv(res_df, file.path(outdir, "deg_results.csv"), row.names = FALSE)
    break
}

vsd <- vst(dds, blind = FALSE)
pca_plot <- plotPCA(vsd, intgroup = c("condition"))
ggsave(file.path(outdir, "pca_plot.png"), pca_plot, width = 8, height = 6, dpi = 150)

deg <- read.csv(file.path(outdir, "deg_results.csv"))
if (nrow(deg) > 0 && "log2FoldChange" %in% colnames(deg) && "padj" %in% colnames(deg)) {
    volcano <- EnhancedVolcano(
        deg,
        lab = deg$gene,
        x = "log2FoldChange",
        y = "padj",
        pCutoff = 0.05,
        FCcutoff = 1.0,
        title = paste("Volcano Plot -", run_id),
        subtitle = "|log2FC| > 1, padj < 0.05"
    )
    ggsave(file.path(outdir, "volcano_plot.png"), volcano, width = 10, height = 8, dpi = 150)

    ma <- ggplot(deg, aes(x = baseMean, y = log2FoldChange)) +
        geom_point(aes(color = padj < 0.05), alpha = 0.6) +
        scale_x_log10() +
        scale_color_manual(values = c("grey", "red")) +
        labs(title = paste("MA Plot -", run_id), x = "Mean of normalized counts", y = "Log2 fold change") +
        theme_minimal() +
        theme(legend.position = "none")
    ggsave(file.path(outdir, "ma_plot.png"), ma, width = 8, height = 6, dpi = 150)

    top_genes <- head(deg$gene[deg$padj < 0.05], 50)
    if (length(top_genes) > 1) {
        mat <- assay(vsd)[rownames(assay(vsd)) %in% top_genes, ]
        pheatmap(
            mat,
            filename = file.path(outdir, "heatmap.png"),
            scale = "row",
            annotation_col = as.data.frame(colData(vsd)[, "condition", drop = FALSE]),
            main = paste("Heatmap -", run_id),
            width = 8,
            height = 10,
            dpi = 150
        )
    }
}

cat("DESeq2 analysis completed for run:", run_id, "\n")
