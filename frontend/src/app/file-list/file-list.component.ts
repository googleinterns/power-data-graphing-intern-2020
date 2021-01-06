import { Component, OnInit } from '@angular/core';
import {
  HttpService,  RecordsResponse,
  ResponseData,
  ResponseFileInfo,
} from '../services/http.service';
import { catchError } from 'rxjs/operators';
import { HttpErrorResponse } from '@angular/common/http';
import { Subscription, throwError } from 'rxjs';
import {FileServiceService} from '../services/file-service.service';

@Component({
  selector: 'app-file-list',
  templateUrl: './file-list.component.html',
  styleUrls: ['./file-list.component.scss']
})
export class FileListComponent implements OnInit {
  fileList: string[] = ['ClockworkMapTests-testMapWear-__J4015_J4002_J1630_J1622_J1633_J4007_J3909_J1623_J3911_J3912_J3901_J1617_J3907_J1607__2020-11-30T19:15:36.525Z.csv'];
  selectedFilename = "";
  constructor(private service: HttpService, private readonly fileService: FileServiceService) { }

  selectFile(file: string){
    this.selectedFilename = file;
    console.log(file);
    this.fileService.updateFilename(file);
  }

  ngOnInit(): void {
    this.fileService.filename.subscribe(filename => {
      this.selectedFilename = filename;
    })
    this.service
      .getFileInfo('/fileinfo')
      .pipe(
        catchError((error: HttpErrorResponse) => {
          if (error.error instanceof ProgressEvent) {
            console.error(error.message)
          } else {
            console.error(error.error);
          }
          return throwError(error);
        })
      )
      .subscribe((response: ResponseFileInfo[]) => {
        for(let fileInfo of response){
          this.fileList.push(fileInfo.name)
        }
      });
  }

}
