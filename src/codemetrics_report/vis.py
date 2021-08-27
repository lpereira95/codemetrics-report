import altair as alt
from codemetrics.vega import vis_ages
from codemetrics.vega import vis_hot_spots


def create_loc_chart(loc_df):
    loc_sum = loc_df.groupby('language').sum().reset_index().melt(
        id_vars=['language']).rename(columns={'variable': 'type', 'value': 'lines'})

    chart = alt.Chart(loc_sum).mark_bar().encode(
        x=alt.X('lines:Q'),
        y=alt.Y('language:N', sort=alt.EncodingSortField(field='lines', op='sum', order='descending')),
        color=alt.Color('type:N', scale=alt.Scale(scheme='accent')),
        tooltip=['lines:Q', 'type:O'],
    ).properties(title='Lines of code')

    return chart


def create_age_chart(ages_df, weeks=52):

    width = 1000
    weeks = list(range(weeks))
    chart = alt.Chart(ages_df).encode(color='language')
    top = chart.mark_bar().\
        encode(x=alt.X('age_agg:O', sort='ascending', title='age in weeks',
                       scale=alt.Scale(domain=weeks)),
               y=alt.Y('count(path):Q', title='Number of files'),
               color=alt.Color('language', scale=alt.Scale(scheme='tableau10')),
               tooltip=['count(path)', 'language']
               ).\
        transform_calculate(age_agg='floor(datum.age / 7)').\
        properties(width=width)
    bottom = chart.mark_tick(size=60, thickness=2, opacity=.3).\
        encode(x=alt.X('age:Q', title='age in days'),
               tooltip='path').properties(width=width)
    chart = alt.vconcat(top, bottom)

    return chart


def create_age_loc_chart(ages_df, height=500, width=500, **kwargs):
    """
    Notes:
        Use `VegaLite` to visualize output.
    """
    return vis_ages(ages_df, height=height, width=width, **kwargs)


def create_hotspots_chart(hspots, width=500, height=500,
                          size_column='complexity', **kwargs):
    """
    Notes:
        Use `VegaLite` to visualize output.
    """
    return vis_hot_spots(hspots, width=width, height=height,
                         size_column=size_column, **kwargs)
