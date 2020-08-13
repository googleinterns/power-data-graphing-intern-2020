import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { HttpService } from '../services/http.service';
import { Subscription, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'raw-preprocess-table',
  templateUrl: './raw-preprocess-table.component.html',
  styleUrls: ['./raw-preprocess-table.component.scss'],
})
export class RawPreprocessTableComponent implements OnInit {
  @Output() message = new EventEmitter<string>();
  subscription: Subscription;
  loading = false;
  names: string[];

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.loadFilenames();
  }

  loadFilenames() {
    this.subscription = this.service
      .getFilenames('/filenames')
      .pipe(
        catchError((error: HttpErrorResponse) => {
          this.message.emit(error.error);
          this.loading = false;
          return throwError(error);
        })
      )
      .subscribe((response: { names: string[] }) => {
        this.names = response.names;
        this.loading = false;
      });
  }
}
