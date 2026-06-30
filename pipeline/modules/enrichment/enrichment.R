#!/usr/bin/env Rscript

suppressPackageStartupMessages({
    library(clusterProfiler)
    library(fgsea)
    library(org.Hs.eg.db)
    library(ggplot2)
    library(dplyr)
    library(tidyr)
})

args <- commandArgs(trailingOnly = TRUE)

deg_path <- sub("--deg=", "", args[grep("--deg", args)])
organism <- sub("--organism=", "", args[grep("--organism", args)])
outdir <- sub("--outdir=", "", args[grep("--outdir", args)])

if (length(outdir) == 0 || outdir == "") outdir <- "./"
if (length(organism) == 0 || organism == "") organism <- "org.Hs.eg.db"
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

set.seed(42)

deg <- read.csv(deg_path)
deg_sig <- deg[which(deg$padj < 0.05 & abs(deg$log2FoldChange) > 1), ]
gene_list <- deg_sig$gene

entrez <- bitr(gene_list, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db)
all_entrez <- bitr(deg$gene, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db)

# GO enrichment
if (!is.null(entrez) && nrow(entrez) > 0) {
    go <- enrichGO(
        gene = entrez$ENTREZID,
        universe = all_entrez$ENTREZID,
        OrgDb = org.Hs.eg.db,
        ont = "ALL",
        pAdjustMethod = "BH",
        pvalueCutoff = 0.05,
        qvalueCutoff = 0.2,
        readable = TRUE
    )
    if (!is.null(go) && nrow(as.data.frame(go)) > 0) {
        write.table(as.data.frame(go), file.path(outdir, "go_enrichment.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)

        p_go <- dotplot(go, split = "ONTOLOGY", showCategory = 10) +
            facet_grid(ONTOLOGY ~ ., scale = "free", space = "free") +
            ggtitle("GO Enrichment")
        ggsave(file.path(outdir, "go_dotplot.png"), p_go, width = 10, height = 8)
    }

    # KEGG enrichment
    kegg <- enrichKEGG(
        gene = entrez$ENTREZID,
        organism = "hsa",
        pAdjustMethod = "BH",
        pvalueCutoff = 0.05,
        qvalueCutoff = 0.2
    )
    if (!is.null(kegg) && nrow(as.data.frame(kegg)) > 0) {
        write.table(as.data.frame(kegg), file.path(outdir, "kegg_enrichment.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)

        p_kegg <- dotplot(kegg, showCategory = 15) +
            ggtitle("KEGG Pathway Enrichment")
        ggsave(file.path(outdir, "kegg_dotplot.png"), p_kegg, width = 10, height = 6)
    }
}

# GSEA
gene_rank <- deg %>%
    mutate(rank = log2FoldChange * -log10(pvalue)) %>%
    arrange(desc(rank))
rank_vec <- setNames(gene_rank$rank, gene_rank$gene)
rank_vec <- rank_vec[is.finite(rank_vec)]

if (requireNamespace("msigdbr", quietly = TRUE)) {
    library(msigdbr)
    hs_hallmark <- msigdbr(species = "Homo sapiens", category = "H") %>%
        split(x = .$gene_symbol, f = .$gs_name)

    gsea_res <- fgsea(
        pathways = hs_hallmark,
        stats = rank_vec,
        minSize = 15,
        maxSize = 500,
        nperm = 10000
    )
    gsea_res <- gsea_res[order(pval), ]
    write.table(as.data.frame(gsea_res), file.path(outdir, "gsea_results.tsv"),
        sep = "\t", quote = FALSE, row.names = FALSE)

    if (nrow(gsea_res[gsea_res$padj < 0.05, ]) > 0) {
        top <- gsea_res[padj < 0.05][order(NES), head(.SD, 1), by = "sign(NES)"]
        for (pathway in head(top$pathway, 6)) {
            p <- plotEnrichment(hs_hallmark[[pathway]], rank_vec) +
                labs(title = pathway) +
                theme_minimal()
            safe_name <- gsub("[^A-Za-z0-9]", "_", pathway)
            ggsave(file.path(outdir, paste0("gsea_", safe_name, ".png")), p, width = 7, height = 5)
        }

        p_gsea_bar <- ggplot(gsea_res[padj < 0.05][order(NES)], aes(x = reorder(pathway, NES), y = NES, fill = NES > 0)) +
            geom_bar(stat = "identity") +
            coord_flip() +
            labs(title = "Hallmark Gene Sets Enriched", x = "", y = "NES") +
            scale_fill_manual(values = c("TRUE" = "#e53e3e", "FALSE" = "#3182ce")) +
            theme_minimal() + theme(legend.position = "none")
        ggsave(file.path(outdir, "gsea_barplot.png"), p_gsea_bar, width = 8, height = 6)
    }
}

cat("Enrichment analysis completed\n")
cat(sprintf("  DEG input: %d, mapped to ENTREZ: %d\n", nrow(deg_sig), ifelse(!is.null(entrez), nrow(entrez), 0)))
