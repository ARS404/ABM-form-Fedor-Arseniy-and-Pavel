import agentpy as ap
import ipysimulate as ips

from ipywidgets import AppLayout

from Models.BaseModel import BaseModel
from Agents.BaseAgent import BaseAgent


parameters = {
    'agents': {
        BaseAgent: 1000,
    },
    'steps': 100,
}


def main():
    model = BaseModel(parameters=parameters)
    control = ips.Control(model, parameters, variables=('t',))
    lineplot = ips.Lineplot(control, 'gini')
    AppLayout(
        left_sidebar=control,
        center=lineplot,
        pane_widths=['125px', 1, 1],
        height='400px'
    )
    result = model.run()
    print(result)


if __name__ == '__main__':
    main()
