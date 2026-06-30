#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(ComplexHeatmap)
    library(circlize)
    library(ggplot2)
    library(dplyr)
    library(tidyr)
})

args <- commandArgs(trailingOnly = TRUE)

count_matrix_path <- sub("--count_matrix=", "", args[grep("--count_matrix", args)])
samplesheet_path <- sub("--samplesheet=", "", args[grep("--samplesheet", args)])
outdir <- sub("--outdir=", "", args[grep("--outdir", args)])

if (length(outdir) == 0 || outdir == "") outdir <- "./"
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

set.seed(42)

count_data <- read.csv(count_matrix_path, row.names = 1, check.names = FALSE)
samplesheet <- read.csv(samplesheet_path, row.names = 1, check.names = FALSE)

common <- intersect(colnames(count_data), rownames(samplesheet))
count_data <- count_data[, common, drop = FALSE]
samplesheet <- samplesheet[common, , drop = FALSE]

# Log2 CPM normalisation
lib_sizes <- colSums(count_data)
cpm <- t(t(count_data + 0.5) / lib_sizes) * 1e6
log2_cpm <- log2(cpm)

# Sample correlation heatmap
cor_mat <- cor(log2_cpm, method = "pearson")
if (ncol(cor_mat) <= 30) {
    cond_colors <- setNames(
        c("#e53e3e", "#3182ce", "#38a169", "#dd6b20", "#805ad5", "#d53f8c"),
        head(unique(samplesheet$condition), 6)
    )
    batch_colors <- setNames(
        c("#2d3748", "#718096"),
        head(unique(samplesheet$batch), 2)
    )
    png(file.path(outdir, "sample_correlation.png"), width = 8, height = 7, units = "in", res = 150)
    ht <- Heatmap(
        cor_mat,
        name = "Pearson r",
        col = colorRamp2(c(0.85, 0.95, 1), c("#1a1a2e", "#0f3460", "#e94560")),
        show_row_dend = TRUE,
        show_column_dend = TRUE,
        column_names_gp = gpar(fontsize = 8),
        row_names_gp = gpar(fontsize = 8),
        top_annotation = HeatmapAnnotation(
            condition = samplesheet$condition,
            batch = samplesheet$batch,
            col = list(
                condition = cond_colors,
                batch = batch_colors
            )
        )
    )
    draw(ht)
    dev.off()
}

# Gene coverage CDF
gene_means <- rowMeans(log2_cpm, na.rm = TRUE)
cdf_df <- data.frame(log2_cpm = sort(gene_means), cum_prob = seq_along(gene_means) / length(gene_means))
p_cov <- ggplot(cdf_df, aes(x = log2_cpm, y = cum_prob)) +
    geom_line(color = "#3182ce", linewidth = 1) +
    labs(title = "Gene Coverage (CDF)", x = "Mean log2 CPM", y = "Cumulative fraction") +
    theme_minimal()
ggsave(file.path(outdir, "gene_coverage.png"), p_cov, width = 7, height = 5)

# PCA variance explained
pca <- prcomp(t(log2_cpm[complete.cases(log2_cpm), ]), center = TRUE, scale. = TRUE)
var_exp <- summary(pca)$importance[2, 1:10] * 100
var_df <- data.frame(PC = factor(paste0("PC", 1:10), levels = paste0("PC", 1:10)), variance = var_exp)
p_var <- ggplot(var_df, aes(x = PC, y = variance)) +
    geom_bar(stat = "identity", fill = "#3182ce", alpha = 0.8) +
    labs(title = "Variance Explained by PCs", x = "Principal Component", y = "Variance (%)") +
    theme_minimal()
ggsave(file.path(outdir, "pca_variance.png"), p_var, width = 6, height = 4)

# PCA coloured by batch
pca_df <- as.data.frame(pca$x)
pca_df$batch <- samplesheet$batch
pca_df$condition <- samplesheet$condition
p_batch <- ggplot(pca_df, aes(x = PC1, y = PC2, color = batch, shape = condition)) +
    geom_point(size = 3, alpha = 0.8) +
    labs(title = "PCA by Batch", x = paste0("PC1 (", round(var_exp[1], 1), "%)"), y = paste0("PC2 (", round(var_exp[2], 1), "%)")) +
    theme_minimal() +
    scale_color_manual(values = c("batch1" = "#3182ce", "batch2" = "#dd6b20"))
ggsave(file.path(outdir, "batch_pca.png"), p_batch, width = 7, height = 5)

cat("QC analysis completed\n")
