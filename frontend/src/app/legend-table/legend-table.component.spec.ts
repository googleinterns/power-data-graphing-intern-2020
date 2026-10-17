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
import { MatCheckboxModule } from '@angular/material/checkbox';

import { LegendTableComponent } from './legend-table.component';

describe('LegendTableComponent', () => {
  let component: LegendTableComponent;
  let fixture: ComponentFixture<LegendTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LegendTableComponent ],
      imports: [ MatCheckboxModule ],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LegendTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should select and unselect all rails via setAll', () => {
    component.records = [
      { id: 0, color: '#000', show: true, data: [], name: 'System', min: 0, max: 10, focusPower: 'N/A' },
      { id: 1, color: '#fff', show: true, data: [], name: 'BTWIFI', min: 0, max: 5, focusPower: 'N/A' },
    ];
    const emitSpy = spyOn(component.showAllChange, 'emit');

    expect(component.isAllSelected()).toBeTrue();
    expect(component.isPartiallySelected()).toBeFalse();

    component.setAll(false);
    expect(component.records.every((r) => !r.show)).toBeTrue();
    expect(component.isAllSelected()).toBeFalse();
    expect(component.isPartiallySelected()).toBeFalse();
    expect(emitSpy).toHaveBeenCalledWith(false);

    component.records[0].show = true;
    expect(component.isPartiallySelected()).toBeTrue();

    component.setAll(true);
    expect(component.records.every((r) => r.show)).toBeTrue();
    expect(component.isAllSelected()).toBeTrue();
    expect(emitSpy).toHaveBeenCalledWith(true);
  });
});
