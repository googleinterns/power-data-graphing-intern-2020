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
    const records = this.records;
    const time_parse = this.time_parse;
    const time_format = this.time_format;

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
        d3.min(records, (d) => this.time_parse(d[0])),
        d3.max(records, (d) => this.time_parse(d[0])),
      ])
      .range([this.chart_padding, this.chart_width - this.chart_padding]);

    const y_scale = d3
      .scaleLinear()
      .domain([0, d3.max(records, (d) => +d[1])])
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

    // Draw Area under the curve
    const area = d3
      .area()
      .defined((d) => +d[1] >= 0)
      .x((d: any) => x_scale(this.time_parse(d[0])))
      .y0(() => y_scale.range()[0])
      .y1((d: any) => y_scale(+d[1]));
    svg.append('path').datum(records).attr('fill', '#F2EEB3').attr('d', area);

    const bisect = d3.bisector((d) => this.time_parse(d[0])).left;

    // Create the circle that travels along the curve of chart
    const focus = svg
      .append('g')
      .append('circle')
      .style('fill', 'none')
      .attr('stroke', 'black')
      .attr('r', 8.5)
      .style('opacity', 0);

    // Create the text that travels along the curve of chart
    const focusText = svg
      .append('g')
      .append('text')
      .attr('opacity', 1)
      .attr('text-anchor', 'left')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', '20px');

    // Draw lines
    const line = d3
      .line()
      .x((d: any) => x_scale(this.time_parse(d[0])))
      .y((d: any) => y_scale(+d[1]));

    svg
      .append('path')
      .datum(records)
      .attr('fill', 'none')
      .attr('stroke', '#F29F05')
      .attr('stroke-width', 2)
      .attr('d', line)
      .attr('opacity', 0.4);

    // Create a rect on top of the svg area: this rectangle recovers mouse position
    svg
      .append('rect')
      .style('fill', 'none')
      .style('pointer-events', 'all')
      .attr('width', this.chart_width - this.chart_padding)
      .attr('height', this.chart_height)
      .on('mouseover', mouseover)
      .on('mousemove', mousemove)
      .on('mouseout', mouseout);

    // What happens when the mouse move -> show the annotations at the right positions.
    function mouseover() {
      focus.style('opacity', 1);
      focusText.style('opacity', 1);
    }

    function mousemove() {
      // recover coordinate we need
      var x0 = x_scale.invert(d3.mouse(this)[0]);
      var i = bisect(records, x0, 1);
      const selectedData = records[i];

      focus
        .attr('cx', x_scale(time_parse(selectedData[0])))
        .attr('cy', y_scale(+selectedData[1]));
      focusText
        .html(
          `x: ${time_format(time_parse(selectedData[0]))} - y: ${
            selectedData[1]
          }`
        )
        .attr('x', x_scale(time_parse(selectedData[0])) + 15)
        .attr('y', y_scale(+selectedData[1]));
    }
    function mouseout() {
      focus.style('opacity', 0);
      focusText.style('opacity', 0);
    }
  }
}
