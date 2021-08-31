import pandas as pd
import math


def truncate(number, decimals=3):
	factor = 10.0 ** decimals
	return math.trunc(float(number) * factor) / factor


def tooltip(kwargs, obj="datum"):
	return {"signal":"'"+"+', ".join(f"{key}: '+{obj}.{value}" for key, value in kwargs.items())}


def extract_loops(links, access=lambda x:x):
	cache = []
	for link in links:
		x, y = access(link)
		new_points = {x,y}
		new_entries = [link]
		l = len(cache)
		for i, (points, entries) in enumerate(reversed(cache)):
			if x in points or y in points:
				new_points.update(points)
				new_entries.extend(entries)
				cache.pop(l-i-1)
		cache.append([new_points, new_entries])
	return [(list(points), entries) for points, entries in cache]


def reindex(indexes, links, points):
	convert = {old:new for new, old in enumerate(indexes)}
	for link in links:
		link["source"] = convert[link["source"]]
		link["target"] = convert[link["target"]]
	new_points = []
	for new, old in enumerate(indexes):
		point = points[old]
		point["index"] = new
		new_points.append(point)
	return links, new_points


def make_graph(
	nodes,
	links,
	source="path",
	target="dependency",
	node_size="code",
	node_color="code",
	node_scheme="greenblue",
	link_size="cochanges",
	link_color="coupling",
	link_scheme="yelloworangered",
	width=800,
	height=600,
	distance=60):

	opacity_hide = 0
	opacity_node = 1
	opacity_link = 0.5

	nodes = nodes.reset_index()[[source, node_size, node_color]]
	active_nodes = pd.concat([links[source], links[target]]).unique()
	active_nodes = pd.DataFrame(active_nodes, columns=[source]).merge(nodes).reset_index()
	links = links.merge(active_nodes).merge(active_nodes, left_on=target, right_on=source)[["index_x", "index_y", link_size, link_color]]

	nodes =[{"name":name,"index":int(index),"size":float(size),"color":truncate(color)} for index,name,size,color in active_nodes.values]
	links = [{"source":int(source),"target":int(target),"size":truncate(size),"color":truncate(color)} for source,target,size,color in links.values]
	access_st = lambda x: (x["source"], x["target"])
	loops = extract_loops(links, access_st)
	loops.sort(key=lambda _:len(_[0]))
	if loops:
		links, nodes = zip(*[reindex(*loop, nodes) for loop in loops])
	else:
		links, nodes = [], []

	data = []
	scales = []
	marks = []
	graph_select = {"input": "radio", "options": list(range(len(loops))), "labels": [f"graph_{i}_{len(_[0])}" for i,_ in enumerate(loops)]}
	for i, (link, node) in enumerate(zip(links, nodes)):
		data.extend([
		{
			"name": f"node_data_{i}",
			"values": node
		},
		{
			"name": f"link_data_{i}",
			"values": link
		}])
		scales.extend([
		{
			"name": f"node_color_{i}",
			"type": "linear",
			"domain": {"data": f"node_data_{i}", "field": "color"},
			"range": {"scheme": node_scheme},
			"domainMin": 0
		},
		{
			"name": f"link_color_{i}",
			"type": "linear",
			"domain": {"data": f"link_data_{i}", "field": "color"},
			"range": {"scheme": link_scheme},
			"domainMin": 0
		},
		{
			"name": f"node_size_{i}",
			"type": "linear",
			"domain": {"data": f"node_data_{i}", "field": "size"},
			"range": [0,{"signal": "max_node_size"}],
			"domainMin": 0
		},
		{
			"name": f"link_size_{i}",
			"type": "linear",
			"domain": {"data": f"link_data_{i}", "field": "size"},
			"range": [0,{"signal": "max_link_size"}],
			"domainMin": 0
		}])
		marks.extend([
		{
			"name": f"nodes_{i}",
			"interactive": {"signal": f"graph_id === {i}"},
			"type": "symbol",
			"zindex": 1,
			"from": {"data": f"node_data_{i}"},
			"on": [
				{
					"trigger": "dragged",
					"modify": "dragged_node",
					"values": "dragged === 1 ? {fx:dragged_node.x, fy:dragged_node.y} : {fx:x(), fy:y()}"
				},
				{
					"trigger": "!dragged",
					"modify": "dragged_node",
					"values": "{fx: null, fy: null}"
				}
			],
			"encode": {
				"enter": {
					"fill": {"scale": f"node_color_{i}", "field": "color"},
					"tooltip": tooltip({source:"name", node_size:"size", node_color:"color"})
				},
				"update": {
					"size": {"scale": f"node_size_{i}", "field": "size"},
					"cursor": {"value": "pointer"},
					"opacity": {"signal": f"graph_id === {i} ? {opacity_node} : {opacity_hide}"}
				}
			},
			"transform": [
				{
					"type": "force",
					"iterations": {"signal": "dynamic ? 300 : 1"},
					"velocityDecay": 0.4,
					"restart": {"signal": "restart"},
					"static": False,
					"forces": [
						{"force": "center", "x": {"signal": "cx"}, "y": {"signal": "cy"}},
						{"force": "collide", "radius": 5},
						{"force": "nbody", "strength": -10},
						{"force": "link", "links": f"link_data_{i}", "distance": {"signal":"link_distance"}}
					]
				}
			]
		},
		{
			"interactive": {"signal": f"graph_id === {i}"},
			"type": "path",
			"from": {"data": f"link_data_{i}"},
			"encode": {
				"enter": {
					"stroke": {"scale": f"link_color_{i}", "field": "color"},
					"tooltip": tooltip({link_size:"size", link_color:"color"})
				},
				"update": {
					"strokeWidth":{"scale": f"link_size_{i}", "field": "size"},
					"opacity": {"signal": f"graph_id === {i} ? {opacity_link} : {opacity_hide}"}
				},
			},
			"transform": [
				{
					"type": "linkpath",
					"shape": "line",
					"sourceX": "datum.source.x",
					"sourceY": "datum.source.y",
					"targetX": "datum.target.x",
					"targetY": "datum.target.y"
				}
			]
		}])


	return {
	"$schema": "https://vega.github.io/schema/vega/v5.json",
	"width": width,
	"height": height,
	"padding": 0,
	"autosize": "none",
	"signals": [
		{"name": "cx", "update": "width / 2"},
		{"name": "cy", "update": "height / 2"},
		{
			"name": "graph_id",
			"bind": graph_select,
			"value": 0
		},
		{
			"name": "dynamic",
			"bind":{"input": "checkbox"},
			"value": "checked"
		},
		{
			"name": "max_node_size",
			"bind":{"input": "range", "min": 0, "max": 10000, "step": 1},
			"value": 1500
		},
		{
			"name": "max_link_size",
			"bind":{"input": "range", "min": 0, "max": 50, "step": 1},
			"value": 10
		},
		{
			"name": "link_distance",
			"bind":{"input": "range", "min": 0, "max": 100, "step": 1},
			"value": distance
		},
		{
			"description": "State variable for active node dragged status.",
			"name": "dragged",
			"value": 0,
			"on": [
				{
					"events": "symbol:mouseout[!event.buttons], window:mouseup",
					"update": "0"
				},
				{"events": "symbol:mouseover", "update": "dragged || 1"},
				{
					"events": "[symbol:mousedown, window:mouseup] > window:mousemove!",
					"update": "2",
					"force": True
				}
			]
		},
		{
			"description": "Graph node most recently interacted with.",
			"name": "dragged_node",
			"value": None,
			"on": [
				{
					"events": "symbol:mouseover",
					"update": "dragged === 1 ? item() : dragged_node"
				}
			]
		},
		{
			"description": "Flag to restart Force simulation upon data changes.",
			"name": "restart",
			"value": False,
			"on": [{"events": {"signal": "dragged"}, "update": "dragged > 1"}]
		}
	],
	"data": data,
	"scales": scales,
	"marks": marks
}
