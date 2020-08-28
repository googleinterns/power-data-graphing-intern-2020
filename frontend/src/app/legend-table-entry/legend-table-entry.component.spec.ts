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

import { LegendTableEntryComponent } from './legend-table-entry.component';

import { RecordsOneChannel, Record } from '../chart/record';
import { By } from '@angular/platform-browser';

describe('LegendCardComponent', () => {
  let component: LegendTableEntryComponent;
  let fixture: ComponentFixture<LegendTableEntryComponent>;

  const mockRecords: Record[] = [
    { time: 1, value: 200 },
    { time: 2, value: 100 },
    { time: 3, value: 100 },
    { time: 4, value: 100 },
    { time: 5, value: 100 },
    { time: 6, value: 100 },
    { time: 7, value: 0 },
  ];
  const mockChannel: RecordsOneChannel = {
    id: 0,
    data: mockRecords,
    color: 'red',
    show: true,
    name: 'sys',
    focusPower: '',
  };

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [LegendTableEntryComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LegendTableEntryComponent);

    component = fixture.componentInstance;
    component.recordsOneChannel = mockChannel;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('test max', () => {
    expect(component.getMax()).toEqual((200).toPrecision(3));
  });
  it('test min', () => {
    expect(component.getMin()).toEqual((0).toPrecision(3));
  });
  it('test avg', () => {
    expect(component.getAvg()).toEqual((100).toPrecision(3));
  });

  it('check box should emit channel and checked', () => {
    component.showChange.subscribe((event: [number, boolean]) => {
      expect(event[0]).toEqual(mockChannel.id);
      expect(event[1]).toEqual(false);
    });

    fixture.debugElement.query(
      By.css('.legend-checkbox')
    ).componentInstance.checked = false;

    component.toggled({ checked: false, source: null });
  });
});
