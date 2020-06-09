import { Component, OnInit } from '@angular/core';
import { GetDataService } from '../services/get-data.service';

@Component({
  selector: 'main-chart',
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss'],
})
export class ChartComponent implements OnInit {
  records: Object;
  loading = false;
  constructor(private service: GetDataService) {}

  ngOnInit(): void {
    this.loading = true;
    this.service.getRecords().subscribe((response) => {
      this.records = response.body;
      this.loading = false;
    });
  }
}
