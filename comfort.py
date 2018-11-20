import numpy
import matplotlib as mpl
import matplotlib.pyplot as plt

# strategy: list of (qty, comfort, unit_cost)

figsize = (16, 9)
dpi = 120

strategy_greedy = [
    (1, 10, 100), # first expansion
    (16, 1, 20), # 1-comfort decorations and wall
    (1, 1, 20), # 1-comfort furniture
    (10, 2, 40), # 2-comfort decorations and wall

    (23, 2, 40), # 2-comfort furniture
    (9, 3, 80), # 3-comfort wall
    (1, 3, 80), # 3-comfort decorations
    (1, 4, 150), # 4-comfort decorations
    
    (1, 12, 500), # second expansion
    (4, 2, 40), # 2-comfort furniture
    (3, 3, 80), # 3-comfort wall
    (1, 4, 150), # 4-comfort wall

    (1, 12, 1000), # third expansion
    (6, 2, 40), # 2-comfort furniture
    (1, 3, 150), # upgrade to 4-comfort furniture
    (11, 2, 150), # upgrade to 4-comfort furniture
    (22, 1, 80), # upgrade to 3-comfort furniture
    ]

strategy_fast_expand = [
    (1, 10, 100), # first expansion
    (16, 1, 20), # 1-comfort decorations and wall
    (10, 2, 40), # 2-comfort decorations and wall
    
    
    (1, 12, 500), # second expansion
    (1, 12, 1000), # third expansion
    (24, 2, 40), # 2-comfort furniture

    (1, 3, 80), # 3-comfort decorations
    (1, 4, 150), # 4-comfort decorations
    (1, 4, 150), # 4-comfort wall
    (4, 2, 40), # 2-comfort furniture
    
    
    (12, 3, 80), # 3-comfort wall
    
    (6, 3, 80), # 3-comfort furniture
    
    
    (12, 2, 150), # upgrade to 4-comfort furniture
    (16, 1, 80), # upgrade to 3-comfort furniture
    ]

strategy_lazy_furniture = [
    (1, 10, 100), # first expansion
    (16, 1, 20), # 1-comfort decorations and wall
    (10, 2, 40), # 2-comfort decorations and wall

    (9, 3, 80), # 3-comfort wall
    (1, 3, 80), # 3-comfort decorations
    (22, 3, 80), # 3-comfort furniture
    (2, 4, 150), # 4-comfort furniture
    (1, 4, 150), # 4-comfort decorations
    
    (1, 12, 500), # second expansion
    (4, 4, 150), # 4-comfort furniture
    (3, 3, 80), # 3-comfort wall
    (1, 4, 150), # 4-comfort wall

    (1, 12, 1000), # third expansion
    (6, 4, 150), # 4-comfort furniture
    ]

strategy_simple_fast = [
    (1, 10, 0), # first expansion
    (50, 2, 40),
    (50, 2, 150),
    ]

strategy_simple_mid = [
    (1, 10, 0), # first expansion
    (40, 2, 40),
    (10, 4, 150),
    (40, 2, 150),
    ]

strategy_simple_slow = [
    (1, 10, 0), # first expansion
    (50, 4, 150),
    ]

def strategy_total(strategy):
    total_cost = sum(qty * unit_cost for (qty, comfort, unit_cost) in strategy)
    total_comfort = sum(qty * comfort for (qty, comfort, unit_cost) in strategy)
    return total_comfort, total_cost

def xp_bonus(comfort):
    return comfort / (comfort + 100.0)

def plot_strategies(strategies, legend):
    max_comfort = max(strategy_total(strategy)[0] for strategy in strategies)
    max_cost = max(strategy_total(strategy)[1] for strategy in strategies)
    
    x = numpy.arange(0.0, max_cost + 1.0)

    fig = plt.figure(figsize=figsize)
    ax = plt.subplot(111)

    ytick_interval = 50.0
    ytick_comfort = numpy.arange(0.0, max_comfort + ytick_interval, ytick_interval)
    ytick_bonus = xp_bonus(ytick_comfort)
    ytick_labels = ['%d' % comfort for comfort in ytick_comfort]
    
    for strategy in strategies:
        y = numpy.zeros_like(x)
        t = 0
        current_comfort = 0
        for qty, comfort, unit_cost in strategy:
            for i in range(qty):
                y[t:t+unit_cost] = xp_bonus(current_comfort)
                t += unit_cost
                current_comfort += comfort
            y[t:] = xp_bonus(current_comfort)
        ax.plot(x, y)
    ax.legend(legend, loc = 'upper left')
    ax.set_xlim(left = 0.0, right = max_cost)
    ax.set_ylim(bottom = 0.0, top = xp_bonus(ytick_comfort[-1]))
    ax.set_yticks(ytick_bonus)
    ax.set_yticklabels(ytick_labels)
    ax.set_xlabel('Cumulative Furniture Coins')
    ax.set_ylabel('Comfort, scaled to XP bonus')
    ax.set_title('Decoration strategies')
    ax.grid()
    plt.savefig('comfort.png', dpi = dpi, bbox_inches = "tight")
        
plot_strategies([strategy_simple_fast, strategy_simple_slow],
                ['Fast strategy: 50x 2-Comfort items, then replace with 50x 4-Comfort items',
                 'Slow strategy: 50x 4-Comfort items'])

