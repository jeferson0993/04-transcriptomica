FROM rocker/tidyverse:4.4

RUN R -e "install.packages(c('optparse', 'DT', 'plotly', 'corrplot'), repos = 'https://cloud.r-project.org')"

RUN R -e "BiocManager::install(c( \
    'DESeq2', \
    'clusterProfiler', \
    'fgsea', \
    'org.Hs.eg.db', \
    'ComplexHeatmap', \
    'circlize', \
    'EnhancedVolcano', \
    'msigdbr' \
), update = FALSE, ask = FALSE)"

WORKDIR /pipeline
COPY . .

CMD ["R"]
