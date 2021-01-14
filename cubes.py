import numpy
import matplotlib as mpl
import matplotlib.pyplot as plt

class Event():
    min_compute_draws = 10000
    
    def __init__(self, name, stage_percents, color, pity = None):
        self.name = name
        self.stage_rates = numpy.array(stage_percents) / 100.0
        self.color = color
        self.pity = pity

    def compute_ccdf(self, max_draws, allow_pity = True):
        max_draws = max(max_draws, self.min_compute_draws)
        # At each stage we will draw until all cards for which
        # that is the best stage are drawn.
        mandatory_stages = numpy.argmax(self.stage_rates, axis = 0)

        num_stages, num_targets = self.stage_rates.shape

        # Whether each target has been drawn, followed by the number of draws that
        # have been consumed.
        event_shape = (2,) * num_targets + (max_draws + 1,)

        # Starting state: nothing drawn.
        event_dist = numpy.zeros(event_shape)
        event_dist[(0,) * num_targets + (0,)] = 1.0

        for stage in range(num_stages):
            stage_rates = self.stage_rates[stage]
            
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
                if draw + 1 == self.pity and allow_pity:
                    continue_dist[1, ...] += continue_dist[0, ...]
                    continue_dist[0, ...] = 0.0
                event_dist[..., draw] = stop_dist
                event_dist[..., draw + 1] += continue_dist

        pdf = event_dist[(1,) * num_targets + (slice(None),)]
        cdf = numpy.cumsum(pdf)
        ccdf = 1.0 - cdf
        return ccdf
    
    def plot(self, ax, legend, max_draws, annotation_offset, is_primary):
        ccdf = self.compute_ccdf(max_draws)
        if is_primary:
            linestyle = '-'
        else:
            linestyle = '--'
        ax.semilogy(2 * numpy.arange(max_draws + 1), 1.0 / ccdf[:max_draws+1], linestyle = linestyle, color = self.color)
        legend.append(self.name)

        if is_primary:
            mean_cubes = 2 * numpy.sum(ccdf)
            mean_cubes_chance = ccdf[int(numpy.ceil(numpy.sum(ccdf)))]
            annotation_text = 'Mean: %0.1f cubes' % mean_cubes

            if self.pity is not None:
                no_pity_ccdf = self.compute_ccdf(max_draws, allow_pity = False)
                no_pity_mean_cubes = 2 * numpy.sum(no_pity_ccdf)
                annotation_text += ' (%0.1f without pity)' % no_pity_mean_cubes
            
            ax.annotate(annotation_text,
                    (mean_cubes, 1.0 / mean_cubes_chance,),
                    (mean_cubes, annotation_offset / mean_cubes_chance),
                    color = self.color,
                    horizontalalignment = 'center',
                    verticalalignment = 'bottom',
                    arrowprops= {'arrowstyle' : '->', 'color' : self.color},
                    zorder = 100)
            


# shortname : longname, stages, color
events = {
    '2%' : Event(
        'One specific 2% ship',
        [
            [2.0],
        ],
        'black'),
    '1.2%pity' : Event(
        '1.2% with 200-draw pity',
        [
            [1.2],
        ],
        'red',
        pity = 200),
    '2ssr_2sr' : Event(
        '2x 2.0% SSR + 2x 2.5% SR',
        [
            [2.0, 2.0, 2.5, 2.5,],
        ],
        'black'),
    '2ssr_3sr' : Event(
        '2x 2.0% SSR + 3x 2.5% SR',
        [
            [2.0, 2.0, 2.5, 2.5, 2.5,],
        ],
        'black'),
    'fw2' : Event(
        'Fallen Wings Rerun',
        [
            [2.0, 2.0, 2.5, 2.5, 5.0],
        ],
        'blue'),
    'nep' : Event(
        'Neptunia',
        [
            [2.25, 2.25, 0.75, 0.75, 3.15, 1.05],
            [0.75, 0.75, 2.25, 2.25, 1.05, 3.15],
        ],
        'purple'),
    'wc2' : Event(
        "Winter's Crown Rerun",
        [
            [2.0, 2.25, 2.5],
        ],
        'red'),
    'vdir2' : Event(
        'Visitors Dyed in Red Rerun (no Zuikaku)',
        [
            [2.0, 2.0, 2.5, 4.0, 6.75, 6.75],
        ],
        'red'),
    'isss' : Event(
        'Ink-Stained Steel Sakura',
        [
            [2.0, 2.0, 2.5, 2.5, 5.0, 5.0],
        ],
        'blue'),
    'isss2' : Event(
        'Ink-Stained Steel Sakura Rerun',
        [
            [1.8, 2.0, 2.0, 2.5, 2.5, 2.5, 5.0, 5.0],
        ],
        'magenta'),
    'isss2_nk' : Event(
        'Ink-Stained Steel Sakura Rerun (no Kawakaze)',
        [
            [2.0, 2.0, 2.5, 2.5, 2.5, 5.0, 5.0],
        ],
        'indigo'),
    'kizuna' : Event(
        'Kizuna AI Only',
        [
            [2.0, 2.0],
        ],
        'pink'),
    'smol' : Event(
        'Smolbotes Only',
        [
            [2.5, 2.5, 2.5],
        ],
        'violet'),
    'kizuna+smol' : Event(
        'Kizuna AI + Smolbotes',
        [
            [2.0, 2.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 2.5, 2.5, 2.5],
        ],
        'red'),
    'as' : Event(
        'Ashen Simulacrum',
        [
            [2.0, 2.0, 2.5,],
        ],
        'steelblue'),
    '1year' : Event(
        '1 Year Anniversary',
        [
            [1.8, 1.8, 2.5,],
        ],
        'darkgoldenrod'),
    'etc' : Event(
        'Empyreal Tragicomedy',
        [
            [2.0, 2.0, 2.5,],
        ],
        'darkgreen'),
    'dc_con_drop' : Event(
        'Divergent Chessboard Rerun construction/drop-only (GZ, Z46, U-47, Hipper, Z25, Z35, Z19)',
        [
            [2.0, 1.5, 2.0, 2.5, 2.5, 2.5, 5.0],
        ],
        'red'),
    'dc_con' : Event(
        'Divergent Chessboard Rerun construction-only (GZ, U-47, Z25)',
        [
            [2.0, 2.0, 2.5,],
        ],
        'darkred'),
    'no_no_avrora' : Event(
        'Northern Overture (no Avrora, no Chapayev)',
        [
            [2.0, 2.0, 2.5, 2.5],
        ],
        'goldenrod'),
    'no_avrora' : Event(
        'Northern Overture (need Avrora, no Chapayev)',
        [
            [1.5, 2.0, 2.0, 2.5, 2.5],
        ],
        'red'),
    'db' : Event(
        "Dreamwaker's Butterfly",
        [
            [1.2, 2.0, 2.5, 2.5, 2.5],
        ],
        'blue',
        pity = 200),
    'shinano' : Event(
        'Shinano',
        [
            [1.2],
        ],
        'cadetblue',
        pity = 200),
    'uiu' : Event(
        "Universe in Unison",
        [
            [2.0, 2.0, 2.0, 2.5, 2.5],
        ],
        'purple',),
    'doa' : Event(
        "Dead or Alive Collab",
        [
            [2.0, 2.0, 2.0, 2.5, 2.5],
        ],
        'salmon',),
}

max_draws = 400

# Plot.

figsize = (16, 9)
dpi = 120

event_shortnames = [
    ('doa', 2.0),
    ('db', 0.45),
    ('2ssr_2sr', 3.0),
]
compare_shortnames = [
    #('nep', 0.5),
]

max_cubes = max_draws * 2

fig = plt.figure(figsize=figsize)
ax = plt.subplot(111)

legend = []

for shortname, annotation_offset in event_shortnames:
    events[shortname].plot(ax, legend, max_draws, annotation_offset, True)
for shortname, annotation_offset in compare_shortnames:
    events[shortname].plot(ax, legend, max_draws, annotation_offset, False)

ax.set_xlabel('Cubes\n(minor lines = 20 cubes = 10 builds)')
ax.set_ylabel('Chance to have constructed all ships')

ax.set_xlim(left = 0, right = max_draws * 2)
ax.set_ylim(bottom = 1.0, top = 600)

ax.set_xticks(numpy.arange(0, max_draws * 2 + 1, 100))
ax.set_xticks(numpy.arange(0, max_draws * 2 + 1, 20), minor = True)

yticks = [5, 10, 20, 50, 100, 200, 500]
ax.set_yticks([2] + yticks)
ax.set_yticklabels(['1 in 2\n(median)'] + ['%d in %d' % (y-1, y) for y in yticks])

ax.grid(which = 'major')
ax.grid(which = 'minor', linewidth=0.25)

ax.set_title('Drawing all %s event ships' % events[event_shortnames[0][0]].name)
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
