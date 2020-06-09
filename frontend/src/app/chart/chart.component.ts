import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { GetDataService } from '../services/get-data.service';
import * as d3 from 'd3';

@Component({
  selector: 'main-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ChartComponent implements OnInit {
  records: any;
  loading = false;

  // Chart size constants
  chart_width = 900;
  chart_height = 700;
  chart_padding = 50;
  time_parse = d3.timeParse('%s');
  time_format = d3.timeFormat('%m/%d-%H:%M');

  constructor(private service: GetDataService) {}

  ngOnInit(): void {
    this.loading = true;
    this.service.getRecords().subscribe((response) => {
      this.records = response.body;
      this.loading = false;
      this.createLineChart();
    });
  }

  createLineChart() {
    // Chart SVG Component
    const svg = d3
      .select('#chart-component')
      .append('svg')
      .attr('width', this.chart_width)
      .attr('height', this.chart_height);

    // Scale
    const x_scale = d3
      .scaleTime()
      .domain([
        d3.min(this.records, (d) => this.time_parse(d[0])),
        d3.max(this.records, (d) => this.time_parse(d[0])),
      ])
      .range([this.chart_padding, this.chart_width - this.chart_padding]);

    const y_scale = d3
      .scaleLinear()
      .domain([0, d3.max(this.records, (d) => +d[1])])
      .range([this.chart_height - this.chart_padding, this.chart_padding]);

    // Create Axis
    const x_axis = d3.axisBottom(x_scale).ticks(5).tickFormat(this.time_format);
    const y_axis = d3.axisLeft(y_scale).ticks(12);
    svg
      .append('g')
      .classed('x-axis', true)
      .attr(
        'transform',
        `translate(0, ${this.chart_height - this.chart_padding})`
      )
      .call(x_axis);
    svg
      .append('g')
      .classed('y-axis', true)
      .attr('transform', `translate(${this.chart_padding},0)`)
      .call(y_axis);

    // Draw lines
    const line = d3
      .line()
      .x((d: any) => x_scale(this.time_parse(d[0])))
      .y((d: any) => y_scale(+d[1]));

    svg
      .append('path')
      .datum(this.records)
      .attr('fill', 'none')
      .attr('stroke', '#448C30')
      .attr('stroke-width', 2)
      .attr('d', line);
  }

  createScatterChart() {
    // Chart SVG Component
    const svg = d3
      .select('#chart-component')
      .append('svg')
      .attr('width', this.chart_width)
      .attr('height', this.chart_height);

    // Create Scales for Chart
    const x_scale = d3
      .scaleLinear()
      .domain([
        d3.min(this.records, (d) => +d[0]),
        d3.max(this.records, (d) => +d[0]),
      ])
      .range([this.chart_padding, this.chart_width - this.chart_padding * 2]);

    const y_scale = d3
      .scaleLinear()
      .domain([0, d3.max(this.records, (d) => +d[1])])
      .range([this.chart_height - this.chart_padding, this.chart_padding]);

    const r_scale = d3
      .scaleSqrt()
      .domain([0, d3.max(this.records, (d) => +d[1])])
      .range([0, 5]);

    // Create Axis
    const x_axis = d3.axisBottom(x_scale).ticks(3);
    svg
      .append('g')
      .classed('x-axis', true)
      .attr(
        'transform',
        `translate(0, ${this.chart_height - this.chart_padding})`
      )
      .call(x_axis);

    const y_axis = d3.axisLeft(y_scale);
    svg
      .append('g')
      .classed('y-axis', true)
      .attr('transform', `translate(${this.chart_padding},0)`)
      .call(y_axis);

    // Fill in data
    svg
      .selectAll('circle')
      .data(this.records)
      .enter()
      .append('circle')
      .attr('cx', (d, i) => {
        return x_scale(+d[0]);
      })
      .attr('cy', (d) => {
        return y_scale(d[1]);
      })
      .attr('r', (d) => r_scale(d[1]))
      .attr('fill', '#d1ab0e');
  }
}
