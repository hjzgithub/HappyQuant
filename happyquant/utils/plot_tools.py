import matplotlib.pyplot as plt

def get_series_plot(plot_series, save_folder_path, save_id):
    plt.figure(figsize=(20, 8))
    plt.plot(plot_series.index, plot_series)
    plt.savefig(f"{save_folder_path}/{save_id}.png")