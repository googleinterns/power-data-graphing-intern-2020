import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RawPreprocessTableComponent } from './raw-preprocess-table.component';

describe('RawPreprocessTableComponent', () => {
  let component: RawPreprocessTableComponent;
  let fixture: ComponentFixture<RawPreprocessTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RawPreprocessTableComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RawPreprocessTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
