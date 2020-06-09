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
  chart_width = 800;
  chart_height = 500;
  chart_padding = 30;

  constructor(private service: GetDataService) {}

  ngOnInit(): void {
    this.loading = true;
    this.service.getRecords().subscribe((response) => {
      this.records = response.body;
      this.loading = false;
      this.createChart();
      console.log(this.records[1]);
    });
  }

  createChart() {
    // Chart SVG Component
    const svg = d3
      .select('#chart-component')
      .append('svg')
      .attr('width', this.chart_width)
      .attr('height', this.chart_height);

    // Create Scales for Chart
    const x_scale = d3
      .scaleLinear()
      .domain([0, this.records.length])
      .range([this.chart_padding, this.chart_width - this.chart_padding * 2]);

    const y_scale = d3
      .scaleLinear()
      .domain([0, d3.max(this.records, (d) => +d[1])])
      .range([this.chart_height - this.chart_padding, this.chart_padding]);

    const r_scale = d3
      .scaleLinear()
      .domain([0, d3.max(this.records, (d) => +d[1])])
      .range([0, 5]);

    // Create Axis
    const x_axis = d3.axisBottom(x_scale);
    svg
      .append('g')
      .classed('x-axis', true)
      .attr(
        'transform',
        `translate(0, ${this.chart_height - this.chart_padding})`
      )
      .call(x_axis);

    // Fill in data
    svg
      .selectAll('circle')
      .data(this.records)
      .enter()
      .append('circle')
      .attr('cx', (d, i) => {
        return x_scale(i);
      })
      .attr('cy', (d) => {
        return y_scale(d[1]);
      })
      .attr('r', (d) => r_scale(d[1]))
      .attr('fill', '#d1ab0e');
  }
}
