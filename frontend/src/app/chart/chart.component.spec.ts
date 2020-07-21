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

import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { from, empty } from 'rxjs';

import { ChartComponent } from './chart.component';
import {
  HttpService,
  STRATEGY,
  RecordsResponse,
} from '../services/http.service';
import { Record } from './record';
import { DebugElement } from '@angular/core';
import { By } from '@angular/platform-browser';
import { tree } from 'd3';

const getMaxMin = (records: number[]) => {
  return [
    records.reduce((left, right) => (left < right ? left : right)),
    records.reduce((left, right) => (left > right ? left : right)),
  ];
};

const generateSingleChannelData = (length: number) => {
  const recordsData: [number, number][] = [];
  for (let index = 0; index < length; index++) {
    recordsData.push([1573149236356988 + index * 2000, Math.random() * 500]);
  }
  const channelData: RecordsResponse[] = [];
  channelData.push({ name: 'sys', data: recordsData });
  return channelData;
};

const generateMultiChannelData = (length: number) => {
  const channelData: RecordsResponse[] = [];
  const channels = ['SYS', 'PPX_ASYS', 'PP1800_SOC'];
  for (const channel of channels) {
    const recordsData: [number, number][] = [];
    for (let index = 0; index < length; index++) {
      recordsData.push([1573149236356988 + index * 2000, Math.random() * 500]);
    }
    channelData.push({ name: channel, data: recordsData });
  }
  return channelData;
};

describe('ChartComponent', () => {
  let component: ChartComponent;
  let fixture: ComponentFixture<ChartComponent>;
  let httpServiceSpy: jasmine.SpyObj<HttpService>;

  const testRecordsSingleChannel = generateSingleChannelData(100);
  const testRecordsMultipleChannel = generateMultiChannelData(100);

  beforeEach(async(() => {
    httpServiceSpy = jasmine.createSpyObj('HttpService', ['getRecords']);

    TestBed.configureTestingModule({
      declarations: [ChartComponent],
      providers: [{ provide: HttpService, useValue: httpServiceSpy }],
    }).compileComponents();
  }));

  beforeEach(() => {
    httpServiceSpy.getRecords.and.callFake(() => {
      return from([testRecordsSingleChannel]);
    });

    fixture = TestBed.createComponent(ChartComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create chart', () => {
    expect(component).toBeTruthy();
  });

  it('svg components should be valid', () => {
    expect(component['brush']).toBeTruthy();
    expect(component['svg']).toBeTruthy();
    expect(component['svgChart']).toBeTruthy();
    expect(component['xAxis']).toBeTruthy();
    expect(component['xScale']).toBeTruthy();
    expect(component['yAxis']).toBeTruthy();
    expect(component['yScale']).toBeTruthy();
    expect(component.zoomIn).toBe(false);
  });

  it('chart x-domain and y-domain should match with data on initialization', () => {
    const expectedDates = testRecordsSingleChannel[0].data.map(
      (record) => record[0]
    );
    // Get timespan of the original records
    const expectedTimespanUnix = getMaxMin(expectedDates);
    // Convert Unix Timestamp to Date Object

    expect(component['xScale'].domain()).toEqual(expectedTimespanUnix);

    const expectedPower = testRecordsSingleChannel[0].data.map(
      (record) => record[1]
    );
    // Get power range of the original records
    const expectedPowerRange = getMaxMin(expectedPower);
    expect(component['yScale'].domain()).toEqual(expectedPowerRange);
  });

  it('updateChartDomain should update chart in accord with this.records', () => {
    // Generate new records
    const newTestRecords = generateSingleChannelData(600);
    const formattedNewTestRecords = newTestRecords[0].data.map((record) => {
      return {
        time: record[0],
        value: record[1],
      } as Record;
    });

    // Load data
    httpServiceSpy.getRecords.and.callFake(() => {
      return from([newTestRecords]);
    });
    component.loadRecords();
    expect(httpServiceSpy.getRecords).toHaveBeenCalled();

    expect(component.records[0].data).toEqual(formattedNewTestRecords);
    expect(component.records[0].name).toEqual(newTestRecords[0].name);

    // Test new x-domain
    const expectedDates = newTestRecords[0].data.map((record) => record[0]);
    const expectedTimespanUnix = getMaxMin(expectedDates);
    expect(component['xScale'].domain()).toEqual(expectedTimespanUnix);

    // Test new y-domain
    const expectedPower = newTestRecords[0].data.map((record) => record[1]);
    const expectedPowerRange = getMaxMin(expectedPower);
    expect(component['yScale'].domain()).toEqual(expectedPowerRange);
  });

  it('strategySwitch should send request with selected strategy', () => {
    const strategies = Object.values(STRATEGY);
    const newStategy =
      strategies[Math.floor(Math.random() * strategies.length)];

    httpServiceSpy.getRecords.and.callFake(
      (
        path: string,
        filename: string,
        strategy: string,
        timespan: number[]
      ) => {
        expect(path).toEqual('/data');
        expect(strategy).toEqual(newStategy.toString());
        expect(timespan).toBeNull();
        return empty();
      }
    );
    component.strategy = newStategy;
    component.strategySwitch();
    expect(httpServiceSpy.getRecords).toHaveBeenCalled();
  });

  it('showLine method should set line opacity', () => {
    component.showLine(['sys', false]);
    expect(
      +component['svgLine'].selectAll('.line-sys').attr('opacity')
    ).toEqual(0);

    component.showLine(['sys', true]);
    expect(
      +component['svgLine'].selectAll('.line-sys').attr('opacity')
    ).toEqual(0.4);
  });

  it('getValueRange should get max and min value on data with attribute show of true', () => {
    const valueRange = component.getValueRange();

    let min, max;
    for (const [_, value] of testRecordsSingleChannel[0].data) {
      if (!min || value < min) min = value;
      if (!max || value > max) max = value;
    }
    expect(valueRange).toEqual([min, max]);
  });

  it('getTimeRange should get max and min time on data with attribute show of true', () => {
    const valueRange = component.getTimeRange();

    let min, max;
    for (const [time, _] of testRecordsSingleChannel[0].data) {
      if (!min || time < min) min = time;
      if (!max || time > max) max = time;
    }
    expect(valueRange).toEqual([min, max]);
  });

  it('fileSwitch should reload svg', () => {
    const initChartSpy = spyOn(component, 'initChart');
    const loadRecordsSpy = spyOn(component, 'loadRecords');
    httpServiceSpy.getRecords.and.callFake(() => {
      return from([[]]);
    });
    component.fileSwitch();

    expect(httpServiceSpy.getRecords).toHaveBeenCalled();
    expect(initChartSpy).toHaveBeenCalled();
    expect(loadRecordsSpy).toHaveBeenCalled();
    expect(component.zoomIn).toEqual(false);
    expect(component['lines']).toEqual({});
    expect(component.records).toEqual([]);
  });
});
