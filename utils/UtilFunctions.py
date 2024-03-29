import matplotlib.pyplot as plt


def draw_plot(plots_data, title, xlabel, ylabel, labels=None, add_x=False, multyplot=False, figsize=(20, 10),
              hlines=None, vlines=None, file=None, logscale=False):
    figure = plt.figure(figsize=figsize)
    if not multyplot:
        plots_data = [plots_data]
    for ind, one_plot in enumerate(plots_data):
        if add_x:
            if labels is not None:
                plt.plot(one_plot[0], one_plot[1], label=labels[ind])
            else:
                plt.plot(one_plot[0], one_plot[1])
        else:
            if labels is not None:
                plt.plot(one_plot, label=labels[ind])
            else:
                plt.plot(one_plot, linewidth=7)

    if hlines is not None:
        for hline in hlines:
            plt.axhline(y=hline[0], color=hline[1], ls=hline[2])
    if vlines is not None:
        for vline in vlines:
            plt.axvline(x=vline[0], color=vline[1], ls=vline[2], linewidth=10)
    if logscale:
        plt.yscale('log')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    # plt.xticks(fontsize=50)
    # plt.yticks(fontsize=50)
    plt.title(title)
    if labels is not None:
        plt.legend()

    if file is None:
        plt.show()
    else:
        plt.savefig(file)

    plt.close(figure)
