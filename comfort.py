# strategy: list of (qty, comfort, unit cost,)

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

strategy_simple_greedy = [
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

strategy_simple_lazy = [
    (1, 10, 0), # first expansion
    (50, 4, 150),
    ]

def compute_strategy_value(strategy):
    total_comfort = 0
    total_cost = 0
    bonus_integral = 0.0
    for qty, comfort, unit_cost in strategy:
        for i in range(qty):
            bonus_integral += unit_cost * total_comfort / (total_comfort + 100)
            total_cost += unit_cost
            total_comfort += comfort
    reference_integral = total_cost * total_comfort / (total_comfort + 100)
    loss_integral = bonus_integral - reference_integral
    print(total_comfort, total_cost, bonus_integral, reference_integral, loss_integral)

compute_strategy_value(strategy_greedy)
compute_strategy_value(strategy_fast_expand)
compute_strategy_value(strategy_lazy_furniture)
compute_strategy_value(strategy_simple_greedy)
compute_strategy_value(strategy_simple_mid)
compute_strategy_value(strategy_simple_lazy)
