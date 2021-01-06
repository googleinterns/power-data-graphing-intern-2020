import {
  Component,
  OnInit,
  Output,
  EventEmitter,
  ViewChild,
} from '@angular/core';
import { HttpService, ResponseFileInfo } from '../services/http.service';
import { Subscription, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { HttpErrorResponse } from '@angular/common/http';
import { MatTableDataSource } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { MatPaginator } from '@angular/material/paginator';

export interface PreprocessEntry {
  name: string;
  status: string;
}

export interface FileInfo {
  name: string;
  preprocessed: boolean;
  loading: boolean;
}

@Component({
  selector: 'raw-preprocess-table',
  templateUrl: './raw-preprocess-table.component.html',
  styleUrls: ['./raw-preprocess-table.component.scss'],
})
export class RawPreprocessTableComponent implements OnInit {
  @Output() message = new EventEmitter<string>();
  subscription: Subscription;
  fileinfo: FileInfo[];
  dataSource: MatTableDataSource<FileInfo>;
  displayedColumns: string[] = ['name', 'status', 'button'];

  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort, { static: true }) sort: MatSort;

  constructor(private service: HttpService) {}

  ngOnInit(): void {
    this.loadFilenames();
  }

  loadFilenames() {
    this.subscription = this.service
      .getFileInfo('/fileinfo')
      .pipe(
        catchError((error: HttpErrorResponse) => {
          if (error.error instanceof ProgressEvent) {
            this.message.emit(error.message);
          } else {
            this.message.emit(error.error);
          }
          return throwError(error);
        })
      )
      .subscribe((response: ResponseFileInfo[]) => {
        this.fileinfo = response.map((singleFileInfo: ResponseFileInfo) => ({
          name: singleFileInfo.name,
          preprocessed: singleFileInfo.preprocessed,
          loading: false,
        }));
        this.dataSource = new MatTableDataSource(this.fileinfo);
        this.dataSource.paginator = this.paginator;
        this.dataSource.sort = this.sort;
      });
  }

  preprocess(filename: string) {
    let file: FileInfo;
    for (const singleFile of this.fileinfo) {
      if (singleFile.name === filename) file = singleFile;
    }

    file.loading = true;
    this.service
      .preprocess('/data', file.name)
      .pipe(
        catchError((error: HttpErrorResponse) => {
          file.loading = false;
          if (error.error instanceof ProgressEvent) {
            this.message.emit(error.message);
          } else {
            this.message.emit(error.error);
          }
          return throwError(error);
        })
      )
      .subscribe(() => {
        file.loading = false;
        file.preprocessed = true;
        this.message.emit('Preprocessing complete!');
      });
  }

  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  showSpinner(loading: boolean) {
    return loading ? 1 : 0;
  }

  showPreprocess(preprocessed: boolean) {
    return preprocessed ? 'yes' : 'no';
  }
}
