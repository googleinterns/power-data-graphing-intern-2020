import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LegendCardComponent } from './legend-card.component';
import { RecordsOneChannel, Record } from '../chart/record';

describe('LegendCardComponent', () => {
  let component: LegendCardComponent;
  let fixture: ComponentFixture<LegendCardComponent>;

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
    data: mockRecords,
    color: 'red',
    show: true,
    name: 'sys',
    focusDate: '',
    focusPower: '',
    focusTime: '',
  };

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [LegendCardComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LegendCardComponent);
    component = fixture.componentInstance;
    component.recordsOneChannel = mockChannel;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('text max', () => {
    expect(component.getMax()).toEqual((200).toPrecision(3));
  });
  it('text min', () => {
    expect(component.getMin()).toEqual((0).toPrecision(3));
  });
  it('text avg', () => {
    expect(component.getAvg()).toEqual((100).toPrecision(3));
  });
});
