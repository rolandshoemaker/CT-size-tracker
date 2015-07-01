import urllib, json, time
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy

known_logs_url = "http://www.certificate-transparency.org/known-logs/all_logs_list.json"

r = urllib.urlopen(known_logs_url)
logs = json.loads(r.read())

# {
# 	"logs": {},
# 	"last_sizes": {}
# }
log_sizes = {}
try:
	size_f = open("log_sizes.json").read()
	log_sizes = json.loads(size_f)
except IOError:
	log_sizes = {"logs": {}, "last_sizes":{}}

now = time.time()
for entry in logs["logs"]:
	r = urllib.urlopen("https://"+entry["url"]+"/ct/v1/get-sth")
	entry_info = json.loads(r.read())
	print(entry["url"] + " " + str(entry_info["tree_size"]))
	if not log_sizes["last_sizes"].get(entry["url"], False):
		log_sizes["logs"][entry["url"]] = []
	else:
		log_sizes["logs"][entry["url"]].append([now, (entry_info["tree_size"] - log_sizes["last_sizes"][entry["url"]])])
	log_sizes["last_sizes"][entry["url"]] = entry_info["tree_size"]

print(log_sizes)

fig = plt.figure(figsize=[12,10])
ax = fig.add_axes([0.1, 0.1, 0.8, 0.75])

for k in log_sizes["logs"]:
	x = [datetime.fromtimestamp(p[0]) for p in log_sizes["logs"][k]]
	y = [p[1] for p in log_sizes["logs"][k]]
	ax.plot_date(x, y, label=k, ls='solid', fmt='')

with open("log_sizes.json", "w") as f:
	json.dump(log_sizes, f)

ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=3, mode="expand", borderaxespad=0.)
fig.savefig("chart.png")
