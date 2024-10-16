library(ggplot2)
library(dplyr)
library(tidyr)

# Read in the CSV file
data <- read.csv("range_sizes_trueMM_parallel_compare_gbm_machina_11_14_23/accuracy_gbm_machina.csv")  

# Reshape the data from wide to long format
data_long <- data %>%
  gather(key = "Model", value = "Accuracy", accuracy_gbm, accuracy_machina, accuracy_nonprimary_gbm, accuracy_machina_nonprimary) %>%
  mutate(Model = case_when(
    Model == "accuracy_gbm" ~ "GBM all",
    Model == "accuracy_machina" ~ "MACHINA all",
    Model == "accuracy_nonprimary_gbm" ~ "GBM non-primary",
    Model == "accuracy_machina_nonprimary" ~ "MACHINA non-primary"
  ))
# Convert 'tree_size' column to a factor for grouping
data_long$tree_size <- factor(data_long$tree_size)
data_long$Model <- factor(data_long$Model, levels = c("GBM all", "MACHINA all", "GBM non-primary", "MACHINA non-primary"))

ggplot(data_long, aes(x = tree_size, y = Accuracy, fill = Model)) +
    stat_boxplot(geom ="errorbar", position = position_dodge(width = 0.9), width = 0.8) +
    # geom_point(color="grey", alpha = 1, size=0.5, position = position_jitter(width = 0.2, height = 0.01)) +
    geom_boxplot(position = position_dodge(width = 0.9), width = 0.8, outlier.shape = NA) +
    labs(x = "Number of leaves in the tree",
        y = "Internal node tissue label accuracy") +
    scale_fill_manual(values = c("orange", "green", "yellow", "lightblue")) +
    scale_y_continuous(limits=c(0.8, 1), breaks = seq(0.8, 1, 0.05)) +
    theme_minimal() + 
    theme(
    axis.text.x = element_text(angle = 0, hjust = 0.5, vjust = 0.5, color = "black", size = 20),
    axis.text.y = element_text(color = "black", size = 20),
    axis.title.y = element_text(margin = margin(t = 0, r = 20, b = 0, l = 0), size = 24),
    axis.title.x = element_text(margin = margin(t = 20, r = 0, b = 0, l = 0), size = 24),
    panel.grid = element_blank(),
    axis.ticks = element_line(color = "black"),
    panel.border = element_rect(fill = NA, color = "black"),
    legend.position = c(1, 0.3),
    legend.justification = c(1, 1),
    legend.title = element_blank(),
    legend.text = element_text(size = 20)
    )

ggsave("range_sizes_trueMM_parallel_compare_gbm_machina_11_14_23/accuracy_gbm_machina.png", dpi = 500)
