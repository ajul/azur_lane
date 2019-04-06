import numpy
import matplotlib as mpl
import matplotlib.pyplot as plt


# shortname : longname, stages, color
events = {
    '2%' : (
        'One 2% ship',
        numpy.array([
            [2.0],
        ]),
        'black'),
    'fw2' : (
        'Fallen Wings Rerun',
        numpy.array([
            [2.0, 2.0, 2.5, 2.5, 5.0],
        ]),
        'blue'),
    'nep' : (
        'Neptunia',
        numpy.array([
            [2.25, 0.75, 0.75, 3.15, 1.05],
            [0.75, 2.25, 2.25, 1.05, 3.15],
        ]),
        'purple'),
    'wc2' : (
        "Winter's Crown Rerun",
        numpy.array([
            [2.0, 2.25, 2.5],
        ]),
        'red'),
    'vdir2' : (
        'Visitors Dyed in Red Rerun (no Zuikaku)',
        numpy.array([
            [2.0, 2.0, 2.5, 4.0, 6.75, 6.75],
        ]),
        'red'),
    'isss' : (
        'Ink-Stained Steel Sakura',
        numpy.array([
            [2.0, 2.0, 2.5, 2.5, 5.0, 5.0],
        ]),
        'violet'),
}

max_calc_draws = 2000
max_plot_draws = 300

def compute_event(event_rates, max_draws):
    event_rates = event_rates / 100.0
    # At each stage we will draw until all cards for which
    # that is the best stage are drawn.
    mandatory_stages = numpy.argmax(event_rates, axis = 0)

    num_stages, num_targets = event_rates.shape

    # Whether each target has been drawn, followed by the number of draws that
    # have been consumed.
    event_shape = (2,) * num_targets + (max_draws + 1,)

    # Starting state: nothing drawn.
    event_dist = numpy.zeros(event_shape)
    event_dist[(0,) * num_targets + (0,)] = 1.0

    for stage in range(num_stages):
        stage_rates = event_rates[stage]
        
        # Which states don't need to continue drawing?
        stop_mask = numpy.zeros((2,) * num_targets, dtype = 'bool')
        mandatory_mask = mandatory_stages == stage
        stop_slice = tuple(1 if mandatory else slice(None) for mandatory in mandatory_mask)
        stop_mask[stop_slice] = True
        
        continue_transition = numpy.zeros((2,) * num_targets * 2)

        for draw_state in numpy.ndindex((2,) * num_targets):
            if stop_mask[draw_state]:
                continue_transition[draw_state + draw_state] = 0.0
            else:
                remainder = 1.0
                for target_index, target_state in enumerate(draw_state):
                    if target_state == 0:
                        next_draw_state = list(draw_state)
                        next_draw_state[target_index] = 1
                        next_draw_state = tuple(next_draw_state)
                        p = stage_rates[target_index]
                        remainder -= p
                        continue_transition[draw_state + next_draw_state] = p
                continue_transition[draw_state + draw_state] = remainder

        for draw in range(max_draws):
            draw_dist = event_dist[..., draw]
            stop_dist = draw_dist * stop_mask
            continue_dist = numpy.tensordot(draw_dist, continue_transition, axes = num_targets)
            event_dist[..., draw] = stop_dist
            event_dist[..., draw + 1] += continue_dist

    pdf = event_dist[(1,) * num_targets + (slice(None),)]
    cdf = numpy.cumsum(pdf)
    ccdf = 1.0 - cdf
    return ccdf

# Plot.

figsize = (16, 9)
dpi = 120
shortname = "isss"

max_calc_cubes = max_calc_draws * 2

fig = plt.figure(figsize=figsize)
ax = plt.subplot(111)

legend = []

event_name, rates, event_color = events[shortname]
ccdf = compute_event(rates, max_calc_draws)
mean_cubes = 2 * numpy.sum(ccdf)
mean_cubes_chance = ccdf[int(numpy.ceil(numpy.sum(ccdf)))]

ax.semilogx(1.0 / ccdf, 2 * numpy.arange(max_calc_draws + 1), linestyle = '-', color = event_color)
legend.append(event_name)

for shortname in ['vdir2', '2%']:
    compare_name, rates, color = events[shortname]
    ccdf = compute_event(rates, max_calc_draws)
    ax.semilogx(1.0 / ccdf, 2 * numpy.arange(max_calc_draws + 1), linestyle = '--', color = color)
    legend.append(compare_name)
    print(numpy.sum(ccdf))

ax.annotate('Mean: %0.1f cubes' % mean_cubes,
            (1.0 / mean_cubes_chance, mean_cubes),
            (1.0 / mean_cubes_chance, mean_cubes + 95),
            color = event_color,
            horizontalalignment = 'center',
            arrowprops= {'arrowstyle' : '->', 'color' : event_color})

ax.set_xlabel('Unluckiness')
ax.set_ylabel('Cubes\n(minor lines = 20 cubes = 10 builds)')

ax.set_xlim(left = 1.0, right = 600)
ax.set_ylim(bottom = 0, top = max_plot_draws * 2)

xticks = [5, 10, 20, 50, 100, 200, 500]
ax.set_xticks([2] + xticks)
ax.set_xticklabels(['1 in 2\n(median)'] + ['1 in %d' % x for x in xticks])

ax.set_yticks(numpy.arange(0, max_plot_draws * 2 + 1, 100))
ax.set_yticks(numpy.arange(0, max_plot_draws * 2 + 1, 20), minor = True)

ax.grid(which = 'major')
ax.grid(which = 'minor', linewidth=0.25)

ax.set_title('Drawing all %s event ships' % event_name)
ax.legend(legend)

plt.savefig('cubes.png', dpi = dpi, bbox_inches = "tight")

# Monte Carlo verification.

verify_trials = 0

if verify_trials > 0:
    verify_histogram = numpy.zeros((max_draws + 1,))

    def do_trial():
        def get_stage(stage):
            stage_rates = event_rates[stage]
            stage_rates = numpy.append(stage_rates, [1.0 - numpy.sum(event_rates[stage])])
            mandatory_mask = mandatory_stages == stage
            return stage_rates, mandatory_mask
            
        stage = 0
        stage_rates, mandatory_mask = get_stage(stage)
        mandatory_mask = mandatory_stages == stage
        drawn = numpy.zeros((num_targets,), dtype = 'bool')

        for draw in range(1, max_draws + 1):
            card = numpy.random.choice(numpy.arange(num_targets + 1), p = stage_rates)
            if card < num_targets:
                drawn[card] = True
            while numpy.all(drawn[mandatory_mask]):
                stage += 1
                if stage >= num_stages:
                    return draw
                stage_rates, mandatory_mask = get_stage(stage)
        return None


    for trial in range(verify_trials):
        draws_needed = do_trial()
        if draws_needed is not None:
            verify_histogram[draws_needed] += 1
        
    verify_histogram /= verify_trials
    verify_ccdf = 1.0 - numpy.cumsum(verify_histogram)

    fig = plt.figure(figsize=figsize)
    ax = plt.subplot(111)
    ax.plot(2 * numpy.arange(max_draws + 1), 100.0 * ccdf, color = 'purple')
    ax.plot(2 * numpy.arange(max_draws + 1), 100.0 * verify_ccdf)
    ax.set_xlabel('Cubes')
    ax.set_ylabel('Chance NOT to have completed (%)')
    ax.set_xlim(left = 0.0, right = max_draws * 2)
    ax.set_ylim(bottom = 0.0, top = 100.0)

    ax.set_xticks(numpy.arange(0, max_cubes + 1, 100))
    ax.set_yticks(numpy.arange(0.0, 100.01, 10.0))

    plt.show()
