// Copyright 2020 Google LLC
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// =============================================================================

import {
  Component,
  OnInit,
  OnDestroy,
  ViewEncapsulation,
  Output,
  EventEmitter,
} from '@angular/core';
import { FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { Location } from '@angular/common';
import { Subscription, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import * as d3 from 'd3';
import {
  HttpService,
  RecordsResponse,
  ResponseData,
  ResponseFileInfo,
} from '../services/http.service';
import { FileServiceService } from '../services/file-service.service';
import { Record, COLORS, RecordsOneChannel, STRATEGY } from './record';
import { HttpErrorResponse } from '@angular/common/http';
import { url } from 'inspector';

@Component({
  selector: 'main-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class ChartComponent implements OnInit, OnDestroy {
  /**
   * The major chart component that draw lines, axis, and all the interaction logics.
   */

  // Component binding
  @Output() message = new EventEmitter<string>();
  filename: string;
  frequency_ratio: string;
  strategyType = STRATEGY;
  subscription: Subscription;
  number = new FormControl(600);
  inactiveChannels = [];
  startTime = 0;
  endTime = 0;
  loading = false;
  records: RecordsOneChannel[] = [];
  strategy = STRATEGY.AVG;
  zoomIn = false;
  fileinfo: ResponseFileInfo[];

  mouseDate = '';
  mouseTime = '';

  // Chart d3 SVG Elements
  private brush: d3.BrushBehavior<unknown>;
  private lines: object = {};
  private svg: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private svgChart: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private svgLine: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private xAxis: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private xScale: d3.ScaleLinear<number, number>;
  private yAxis: d3.Selection<SVGGElement, unknown, HTMLElement, any>;
  private yScale: d3.ScaleLinear<number, number>;

  // Chart size constants
  isLeft = true;
  isLockLegend = false;
  animationDuration = 500;
  chartHeight = 500;
  chartMargin = 70;
  chartPadding = 10;
  chartWidth = 1100;
  labelSize = 10;
  labelPadding = 5;
  svgPadding = 10;
  timeFormat = (time: number) => {
    const timeParse = d3.timeParse('%Q');
    const timeFormat = d3.timeFormat('%M:%S.%L');
    const fineTimeFormat = d3.timeFormat(':%S.%L');
    const upperDate = timeParse(Math.floor(time / 1000).toString());
    const xExtent = this.getTimeRange();

    if (xExtent[1] - xExtent[0] >= 1e6) {
      this.svgChart.select('.x-axis-legend').text('Time (m:s.ms)');
      return timeFormat(upperDate);
    }

    this.svgChart.select('.x-axis-legend').text('Time (:s.ms.µs)');
    return fineTimeFormat(upperDate) + '.' + Math.floor(time % 1000);
  };

  constructor(private service: HttpService, private readonly router: Router, private readonly location: Location, private readonly fileService: FileServiceService) {
    const urlParams = new URLSearchParams(window.location.search);
    const strategy = urlParams.get("strategy");
    const number = urlParams.get("number");
    const channel = urlParams.get("inactiveChannels");
    const stTime = urlParams.get("startTime");
    const endTime = urlParams.get("endTime");
    console.log(stTime);
    if (!isNaN(stTime)) {
      this.startTime = Number.parseFloat(stTime);
    }
    if (!isNaN(endTime)) {
      this.endTime = Number.parseFloat(endTime);
    }
    if (channel && typeof channel === "string") {
      if (channel !== "null") {
        this.inactiveChannels = channel.split(",");
      }
    }
    if (strategy && (<any>Object).values(STRATEGY).includes(strategy)) {
      this.strategy = strategy as STRATEGY;
    }
    if (number && !isNaN(Number(number))) {
      this.number = new FormControl(Number(number));
    }
  }
  ngOnInit(): void {
    this.initChart();
    //this.loadFilenames();
    this.fileService.filename.subscribe(file => {
      this.filename = file;
      this.fileSwitch();
    });
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  loadFilenames() {
    if (this.loading) this.subscription.unsubscribe();
    this.loading = true;
    this.subscription = this.service
      .getFileInfo('/fileinfo')
      .pipe(
        catchError((error: HttpErrorResponse) => {
          this.loading = false;
          if (error.error instanceof ProgressEvent) {
            this.message.emit(error.message);
          } else {
            this.message.emit(error.error);
          }
          return throwError(error);
        })
      )
      .subscribe((response: ResponseFileInfo[]) => {
        this.fileinfo = response;
        console.log("File fetched from response correctly")
        this.loading = false;
      });
  }

  loadRecords(timespan?: number[]) {
    console.log("this method is triggered");
    if (this.loading) this.subscription.unsubscribe();
    this.loading = true;
    this.subscription = this.service
      .getRecords(
        '/data',
        this.filename,
        this.strategy,
        this.number.value,
        timespan
      )
      .pipe(
        catchError((error: HttpErrorResponse) => {
          if (error.error instanceof ProgressEvent) {
            this.message.emit(error.message);
          } else {
            this.message.emit(error.error);
          }
          this.loading = false;
          return throwError(error);
        })
      )
      .subscribe((response: RecordsResponse) => {
        if (this.records.length === 0) {
          this.records = response.data.map(
            (channel: ResponseData, index: number) => {
              const recordsOneChannel = {
                color: COLORS[index],
                data: channel.data.map((d: [number, number]) => {
                  return {
                    time: d[0],
                    value: d[1],
                  } as Record;
                }),
                name: channel.name,
                show: true,
                focusPower: 'N/A',
                id: index,
              };
              return recordsOneChannel;
            }
          );
          for (let [index, channel] of this.inactiveChannels.entries()) {
            if (channel > this.records.length || isNaN(channel)) {
              this.inactiveChannels.splice(index, 1);
              this.updateUrl();
              console.error("Unable to set channels, active channel index is bigger than the maximum channel number");
            } else {
              this.records[channel].show = false;
            }
          }
        } else {
          for (const recordsOneChannel of this.records) {
            let newDataArrived = false;

            for (const channel of response.data) {
              if (recordsOneChannel.name !== channel.name) continue;
              newDataArrived = true;
              recordsOneChannel.data = channel.data.map(
                (d: [number, number]) => {
                  return {
                    time: d[0],
                    value: d[1],
                  } as Record;
                }
              );
            }
            if (!newDataArrived) {
              recordsOneChannel.data = [];
              recordsOneChannel.focusPower = 'N/A';
              this.mouseDate = '';
              this.mouseTime = '';
            }
          }
        }
        this.frequency_ratio =
          +(response.frequency_ratio * 100).toPrecision(5) + '%';

        this.loading = false;
        this.updateChartDomain();
      });
  }

  initChart() {
    // Chart SVG Component
    this.svg = d3
      .select('#chart-component')
      .append('svg')
      .attr('width', this.chartWidth)
      .attr('height', this.chartHeight);

    // Add a clipPath: everything out of this area won't be drawn.
    this.svg
      .append('defs')
      .append('svg:clipPath')
      .attr('id', 'clip')
      .append('svg:rect')
      .attr('width', this.chartWidth - this.chartMargin * 2)
      .attr('height', this.chartHeight)
      .attr('x', this.chartMargin)
      .attr('y', 0);

    // Create the chart variable: where both the chart and the brush take place
    this.svgChart = this.svg.append('g').attr('clip-path', 'url(#clip)');

    // Scales
    this.xScale = d3
      .scaleLinear()
      .domain(this.getTimeRange())
      .range([
        this.chartMargin + this.chartPadding,
        this.chartWidth - this.chartMargin - this.chartPadding,
      ]);

    this.yScale = d3
      .scaleLinear()
      .domain(this.getValueRange())
      .range([
        this.chartHeight - this.chartMargin - this.chartPadding,
        this.chartMargin + this.chartPadding,
      ]);

    // Create Axis
    this.xAxis = this.svg
      .append('g')
      .classed('x-axis', true)
      .attr('transform', `translate(0, ${this.chartHeight - this.chartMargin})`)
      .call(d3.axisBottom(this.xScale));

    this.yAxis = this.svg
      .append('g')
      .classed('y-axis', true)
      .attr('transform', `translate(${this.chartMargin},0)`)
      .call(d3.axisLeft(this.yScale));

    // Create x axis legend
    this.svgChart
      .append('g')
      .append('text')
      .classed('x-axis-legend', true)
      .attr('text-anchor', 'left')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', '10px')
      .attr('opacity', 0.5)
      .attr('x', (this.chartWidth - this.chartMargin) / 2)
      .attr('y', this.chartHeight - this.chartMargin / 2)
      .text('Time (m:s.ms)');

    // Create y axis legend
    this.svgChart
      .append('g')
      .append('text')
      .classed('y-axis-legend', true)
      .attr('text-anchor', 'left')
      .attr('transform', 'rotate(-90)')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', '10px')
      .attr('opacity', 0.5)
      .attr('x', -this.chartMargin * 2)
      .attr('y', this.chartMargin + this.chartPadding * 2)
      .text('Power (mW)');

    this.svgLine = this.svgChart.append('g');
    this.svgChart.append('g').classed('labels-background', true).append('rect');
    this.svgChart.append('g').classed('labels', true);

    /**
     * Sets time legend and value overlays as mouse hover on the chart.
     * To be bind with brush event.
     * @param container The container DOM element that contains the SVG area.
     */
    const setFocus = (container: d3.ContainerElement) => {
      // Recover coordinate of cursor.
      const mouseFocus = this.xScale.invert(d3.mouse(container)[0]);
      if (mouseFocus === undefined) return;

      const timeParse = d3.timeParse('%Q');
      const dateFormat = d3.timeFormat('%Y %b %d');
      const timeFormat = d3.timeFormat('%H:%M:%S.%L');

      for (const recordsOneChannel of this.records) {
        if (!recordsOneChannel.show) continue;
        let selectedData = recordsOneChannel.data[0];
        for (const record of recordsOneChannel.data) {
          selectedData =
            Math.abs(selectedData.time - mouseFocus) <
              Math.abs(record.time - mouseFocus)
              ? selectedData
              : record;
        }
        if (!selectedData) continue;

        const upperDate = timeParse(
          Math.floor(selectedData.time / 1000).toString()
        );

        // Sets focus point.
        this.svgLine
          .select('.' + this.getChannelCircleClassName(recordsOneChannel.id))
          .style('opacity', 1)
          .attr('cx', this.xScale(selectedData.time))
          .attr('cy', this.yScale(selectedData.value));

        this.svg
          .select('.' + this.getFocusTextClassName(recordsOneChannel.id))
          .attr('opacity', 1)
          .attr('x', this.xScale(selectedData.time))
          .attr('y', this.yScale(selectedData.value) - this.chartPadding)
          .text(selectedData.value.toString());

        recordsOneChannel.focusPower = selectedData.value.toString();
        this.mouseDate = dateFormat(upperDate);
        this.mouseTime =
          timeFormat(upperDate) + '.' + Math.floor(mouseFocus % 1000);
      }
      const duration = this.xScale.domain()[1] - this.xScale.domain()[0];

      if (!this.isLockLegend) {
        if (mouseFocus < this.xScale.domain()[0] + duration / 4)
          this.isLeft = true;
        if (mouseFocus > this.xScale.domain()[0] + (duration * 3) / 4)
          this.isLeft = false;
      }
      this.setLegend();
    };

    // Brush functionality
    this.brush = d3
      .brushX()
      .extent([
        [this.chartMargin, this.chartMargin],
        [
          this.chartWidth - this.chartMargin,
          this.chartHeight - this.chartMargin,
        ],
      ])

      .on('end', () => {
        this.interactChart.bind(this)();
        this.removeFocus();
      })

      .on('brush', mousemove);

    // Mouse over displaying text
    this.svgChart
      .append('g')
      .attr('class', 'brush')
      .call(this.brush)
      .on('mousemove', mousemove)
      .on('mouseout', () => {
        if (this.isLockLegend) return;
        this.removeFocus();
      });

    function mousemove() {
      setFocus(this);
    }
  }

  removeFocus = () => {
    for (const recordsOneChannel of this.records) {
      this.svgLine
        .select('.' + this.getChannelCircleClassName(recordsOneChannel.id))
        .transition()
        .style('opacity', 0);

      this.svg
        .select('.' + this.getFocusTextClassName(recordsOneChannel.id))
        .transition()
        .attr('opacity', 0);

      this.mouseDate = '';
      this.mouseTime = '';
    }

    this.svg
      .select('.labels')
      .selectAll('rect')
      .transition()
      .attr('opacity', 0);
    this.svg
      .select('.labels')
      .selectAll('text')
      .transition()
      .attr('opacity', 0);
    this.svg
      .select('.labels-background')
      .select('rect')
      .transition()
      .attr('opacity', 0);
  };

  lockLegend() {
    this.isLockLegend = !this.isLockLegend;
  }

  /**
   * Loads data and rescale chart when zoom-in/out
   */
  interactChart() {
    const extent = d3.event.selection;
    if (!extent) return;

    const selectedTimeSpan = [
      this.xScale.invert(extent[0]),
      this.xScale.invert(extent[1]),
    ];

    // This remove the grey brush area as soon as the selection has been done
    this.svgChart.select('.brush').call(this.brush.move, null);

    // Update axis, line and area position, and load new data with the range
    this.zoomIn = true;

    if (selectedTimeSpan[0] >= selectedTimeSpan[1]) return;
    if (this.filename === undefined) {
      this.message.emit('Please select a file.');
      return;
    }
    this.startTime = selectedTimeSpan[0];
    this.endTime = selectedTimeSpan[1];
    this.loadRecords(selectedTimeSpan);
    this.updateUrl();

    this.svgChart.on('dblclick', () => {
      // Reset scale domain
      this.resetChart();
    });
  }

  resetChart(){
    this.zoomIn = false;
    this.loadRecords();
    this.startTime = 0;
    this.endTime = 0;
    this.updateUrl();
  }

  /**
   * Sets text and labels of side legend
   */
  setLegend() {
    const legendText: string[] = [];
    const legendLabels: string[] = [];
    // The list of legend text to show.
    for (const recordsOnechannel of this.records) {
      if (recordsOnechannel.show) {
        legendText.push(
          `${recordsOnechannel.name}: ${recordsOnechannel.focusPower}`
        );
        legendLabels.push(recordsOnechannel.color);
      }
    }
    legendText.push(this.mouseDate);
    legendText.push(this.mouseTime);

    let backgroundWidth = -1;
    for (const text of legendText)
      backgroundWidth =
        backgroundWidth > text.length ? backgroundWidth : text.length;
    backgroundWidth = backgroundWidth * 7;
    const backgroundHeight =
      legendText.length * (this.labelSize + this.labelPadding) +
      this.labelPadding * 2;

    // Calculate positions of the legend.
    const backgroundX = this.isLeft
      ? this.chartWidth - this.chartMargin - backgroundWidth
      : this.chartMargin + this.chartPadding;
    const backgroundY = 100;

    const labelX = this.isLeft
      ? this.chartWidth -
      this.chartMargin -
      this.chartPadding -
      this.labelPadding
      : this.chartMargin + this.chartPadding + this.labelPadding * 2;
    const labelTextX = this.isLeft
      ? this.chartWidth -
      this.chartMargin -
      this.chartPadding -
      this.labelPadding * 2
      : this.chartMargin +
      this.chartPadding * 2 +
      this.labelSize +
      this.labelPadding * 2;

    // The background of the legend.
    this.svgChart
      .select('.labels-background')
      .select('rect')
      .attr('x', backgroundX)
      .attr('y', backgroundY - this.labelPadding)
      .attr('height', backgroundHeight)
      .attr('width', backgroundWidth)
      .attr('fill', 'white')
      .attr('opacity', 1)
      .attr('rx', 15);

    // The colored rectanglar label of the legend.
    const labels: any = this.svgChart
      .select('.labels')
      .selectAll('rect')
      .data(legendLabels);
    labels
      .enter()
      .append('rect')
      .merge(labels)
      .attr('x', labelX)
      .attr(
        'y',
        (_, i) => backgroundY + (this.labelSize + this.labelPadding) * i
      )
      .attr('height', this.labelSize)
      .attr('width', this.labelSize)
      .attr('opacity', 1)
      .style('fill', (d: string) => d);

    // The name text of the legend.
    const labelNames: any = this.svgChart
      .select('.labels')
      .selectAll('text')
      .data(legendText);
    labelNames
      .enter()
      .append('text')
      .merge(labelNames)
      .attr('x', labelTextX)
      .attr(
        'y',
        (_, i) =>
          backgroundY +
          (this.labelSize + this.labelPadding) * i +
          this.labelSize -
          2
      )
      .attr('font-size', this.labelSize + 'px')
      .attr('opacity', 1)
      .text((d: string) => d)
      .attr('text-anchor', this.isLeft ? 'end' : 'start');
  }

  /**
   * Scales or rescales the chart wrt lines to be shown.
   */
  updateChartDomain() {
    this.removeFocus();

    const xExtent = this.getTimeRange();
    const yExtent = this.getValueRange();

    this.xScale.domain(xExtent);
    this.yScale.domain(yExtent);
    this.xAxis
      .transition()
      .duration(this.animationDuration)
      .call(d3.axisBottom(this.xScale).ticks(7).tickFormat(this.timeFormat));
    this.yAxis
      .transition()
      .duration(this.animationDuration)
      .call(d3.axisLeft(this.yScale).tickFormat(d3.format('.3')));

    for (const recordsOneChannel of this.records) {
      if (!this.lines[recordsOneChannel.name]) {
        // Initialize focus line.
        const line = d3
          .line()
          .x((d: any) => this.xScale(d.time))
          .y((d: any) => this.yScale(d.value));

        // Assigns line genrerator for current channel.
        this.lines[recordsOneChannel.name] = line;

        // Creates lines svg component for current channel.
        this.svgLine
          .append('path')
          .classed(this.getChannelLineClassName(recordsOneChannel.id), true)
          .attr('fill', 'none')
          .attr('stroke', recordsOneChannel.color)
          .attr('stroke-width', 2)
          .datum(recordsOneChannel.data as any)
          .attr('d', line)
          .attr('opacity', 0.6);

        // Creates focus circle svg component for current channel.
        this.svgLine
          .append('g')
          .append('circle')
          .classed(this.getChannelCircleClassName(recordsOneChannel.id), true)
          .style('fill', recordsOneChannel.color)
          .attr('stroke', recordsOneChannel.color)
          .attr('r', 2)
          .attr('opacity', 0);

        // Creates focus power value text svg component for current channel.
        this.svg
          .append('g')
          .append('text')
          .classed(this.getFocusTextClassName(recordsOneChannel.id), true)
          .attr('text-anchor', 'right')
          .attr('alignment-baseline', 'right')
          .attr('font-size', '10px')
          .attr('pointer-events', 'none')
          .attr('opacity', 0);
      } else {
        // Update the data associated with this channel
        this.svgLine
          .select('.' + this.getChannelLineClassName(recordsOneChannel.id))
          .datum(recordsOneChannel.data as any)
          .transition()
          .duration(this.animationDuration)
          .attr('d', this.lines[recordsOneChannel.name]);
      }
    }
  }

  /**
   * Reloads data when downsample strategy is switched, keeping original zoom-in level.
   */
  configSwitch() {
    if (this.filename === undefined) {
      this.message.emit('Please select a file.');
      return;
    }
    this.updateUrl();
    this.loadRecords(this.zoomIn ? this.getTimeRange() : null);
  }

  /**
   * Reloads data and re-initialize chart component when switching to another experiment.
   */
  fileSwitch() {
    this.updateUrl();
    this.lines = {};
    this.records = [];
    this.zoomIn = false;
    d3.select('#chart-component').selectAll('*').remove();
    this.initChart();
    if (this.startTime < this.endTime && this.endTime != 0) {
      this.zoomIn = true;
      this.loadRecords([this.startTime, this.endTime]);
    } else {
      this.loadRecords();
    }

  }

  updateUrl() {
    const url = this.router
      .createUrlTree([window.location.pathname], {
        queryParams: {
          'filename': this.filename,
          'strategy': this.strategy,
          'number': this.number.value,
          'inactiveChannels': this.inactiveChannels.toString() || "null",
          'startTime': this.startTime || 0,
          'endTime': this.endTime || 0,
        }
      }).toString();
    this.location.go(url);
  }

  /**
   * Get the class name for the lines.
   * @param channel The name of the channel.
   */
  getChannelLineClassName(id: number) {
    return 'line' + '-' + id;
  }

  /**
   * Get the class name for the focus circle.
   * @param channel The name of the channel.
   */
  getChannelCircleClassName(id: number) {
    return 'circle' + '-' + id;
  }

  /**
   * Get the class name for the focus text.
   * @param channel The name of the channel.
   */
  getFocusTextClassName(id: number) {
    return 'focus-text' + '-' + id;
  }

  /**
   * Get the global max and min time for all channels
   */
  getTimeRange() {
    let min, max;
    for (const recordsOneChannel of this.records) {
      if (!recordsOneChannel.show) continue;
      for (const record of recordsOneChannel.data) {
        if (min === undefined || record.time < min) min = record.time;
        if (max === undefined || record.time > max) max = record.time;
      }
    }
    return [min, max] as number[];
  }

  /**
   * Get the global max and min value for all channels
   */
  getValueRange() {
    let min, max;
    for (const recordsOneChannel of this.records) {
      if (!recordsOneChannel.show) continue;
      for (const record of recordsOneChannel.data) {
        if (min === undefined || record.value < min) min = record.value;
        if (max === undefined || record.value > max) max = record.value;
      }
    }
    return [min, max] as number[];
  }

  /**
   * Shows or hides the channel when toggle the checkbox.
   * @param event The channel name and to show or to hide.
   */
  showLine(event: [number, boolean]) {
    if (event[1]) {
      this.svgLine
        .selectAll('.' + this.getChannelLineClassName(event[0]))
        .attr('opacity', 0.6);
      if (this.inactiveChannels.includes(event[0].toString())) {
        this.inactiveChannels.splice(this.inactiveChannels.indexOf(event[0].toString()), 1);
        this.updateUrl();
      }
    } else {
      this.svgLine
        .selectAll('.' + this.getChannelLineClassName(event[0]))
        .attr('opacity', 0);
      if (!this.inactiveChannels.includes(event[0].toString())) {
        this.inactiveChannels.push(event[0].toString());
        this.updateUrl();
      }
    }
    this.updateChartDomain();
  }
}
