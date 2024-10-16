library(ggplot2)
library(dplyr)

# Path to the CSV file
file_path <- "range_sizes_trueMM_parallel_compare_gbm_machina_11_14_23/time_gbm_machina.csv"

# Read the CSV file
data <- read.csv(file_path)

# # Calculate the ratio of machina_seconds to gbm_seconds
# data_ratio <- data %>%
#   mutate(ratio = machina_seconds / gbm_seconds)

# Reshape the data from wide to long format
data_long <- data %>%
  gather(key = "Model", value = "Seconds", gbm_seconds, machina_seconds) %>%
  mutate(Model = case_when(
    Model == "gbm_seconds" ~ "GBM",
    Model == "machina_seconds" ~ "MACHINA"
  ))
# Convert 'tree_size' column to a factor for grouping
# data_long$tree_size <- factor(data_long$tree_size)

data_summary <- data_long %>%
    group_by(tree_size, Model) %>%
    summarise(mean_seconds = mean(Seconds))

# Plotting
ggplot(data_summary, aes(x = tree_size, y = mean_seconds, color = Model, fill = Model)) +
    # stat_boxplot(geom ="errorbar", position = position_dodge(width = 0.9), width = 0.8) +
    # geom_boxplot(position = position_dodge(width = 0.9), width = 0.8, outlier.size = 1) +
    geom_line(size = 1.5) +
    labs(x = "Number of leaves in the tree",
        y = "Average runtime (seconds)") +
    scale_fill_manual(values = c("orange", "green")) +
    scale_y_continuous(limits=c(0, 600), breaks = seq(0, 600, 100)) +
    scale_x_continuous(limits=c(100, 700), breaks = seq(0, 700, 100)) +
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

ggsave("range_sizes_trueMM_parallel_compare_gbm_machina_11_14_23/time_plot.png", dpi = 500)