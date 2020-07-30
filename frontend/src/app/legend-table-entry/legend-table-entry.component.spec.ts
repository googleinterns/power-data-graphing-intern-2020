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
    data: mockRecords,
    color: 'red',
    show: true,
    name: 'sys',
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
    component.showChange.subscribe((event: [string, boolean]) => {
      expect(event[0]).toEqual(mockChannel.name);
      expect(event[1]).toEqual(false);
    });

    fixture.debugElement.query(
      By.css('.legend-checkbox')
    ).componentInstance.checked = false;

    component.toggled({ checked: false, source: null });
  });
});
