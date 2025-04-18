<template>
  <div class="flex flex-col bg-blue-100 rounded-lg shadow-lg mx-auto p-4 w-full max-w-md">
    <div ref="chart" class="flex justify-center items-center">
      <!-- Graphique -->
    </div>
    <span class="text-center text-gray-600 text-sm">{{ title }}</span>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "PieChart",
  props: {
    data: {
      type: Array,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
  },
  mounted() {
    this.drawChart();
  },
  watch: {
    data(newData) {
      // Redraw the chart when data prop changes
      this.drawChart();
    },
  },
  methods: {
    drawChart() {
      // Remove any previous elements (important for reactivity)
      d3.select(this.$refs.chart).selectAll("*").remove();

      const data = this.data;
      const containerSize = this.$refs.chart.offsetWidth;
      const width = containerSize;
      const height = containerSize;
      const radius = Math.min(width, height) / 2;

      // Create the SVG element
      const svg = d3
        .select(this.$refs.chart)
        .append("svg")
        .attr("viewBox", `0 0 ${width} ${height + 50}`)
        .attr("preserveAspectRatio", "xMinYMin meet")
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

      // Define color scale
      const color = d3.scaleOrdinal(d3.schemeCategory10);

      // Define pie chart layout
      const pie = d3.pie().value((d) => d.value);
      const data_ready = pie(data);

      // Define the arc generator
      const arc = d3.arc().innerRadius(0).outerRadius(radius);

      // Draw the arcs (pie slices)
      svg
        .selectAll("path")
        .data(data_ready)
        .enter()
        .append("path")
        .attr("d", arc)
        .attr("fill", (d) => color(d.data.label))
        .attr("stroke", "black")
        .style("stroke-width", "2px")
        .style("opacity", 0.7);

      // Add labels inside the pie slices
      const labelArc = d3.arc().innerRadius(radius / 2).outerRadius(radius);
      svg
        .selectAll("text")
        .data(data_ready)
        .join("text")
        .attr("transform", (d) => `translate(${labelArc.centroid(d)})`)
        .attr("text-anchor", "middle")
        .attr("class", "text-sm font-medium text-black") // Tailwind classes
        .text((d) => `${d.data.value}`);

      // Add legend
      const legend = d3
        .select(this.$refs.chart)
        .append("div")
        .attr("class", "legend flex flex-wrap justify-center sm:justify-between mt-4");

      legend
        .selectAll("div")
        .data(data)
        .join("div")
        .attr("class", "flex items-center mb-2 sm:mb-0 mr-4")
        .html(
          (d) =>
            `<div class="w-4 h-4" style="background-color: ${color(d.label)}; margin-left: 8px; margin-right: 4px"></div> <span class="text-sm font-medium">${d.label}</span>`
        );
    },
  },
};
</script>
