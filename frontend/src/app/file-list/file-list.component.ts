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
import { Router } from '@angular/router';
import { Location } from '@angular/common';

@Component({
  selector: 'app-file-list',
  templateUrl: './file-list.component.html',
  styleUrls: ['./file-list.component.scss']
})
export class FileListComponent implements OnInit {
  fileList: string[] = [];
  displayList: string[] = [];
  selectedFilename = "";
  loading = false;
  loadingError = false;
  constructor(private service: HttpService, private readonly fileService: FileServiceService,private readonly location: Location, private readonly router: Router) {
   }

  selectFile(file: string){
    this.selectedFilename = file;
    this.updateUrl();
    this.fileService.updateFilename(file);
  }

  searchFile(event: any){
    const keyword = event.target.value.toLowerCase();
    const keywords = keyword.split(" ");
    this.displayList = [];
    for(let file of this.fileList){
      for(let i=0;i<keywords.length;i++){
        if(!file.toLowerCase().includes(keywords[i])){
          break;
        }
        if(i===keywords.length-1){
          this.displayList.push(file);
        }
      }
    }
    if(this.displayList.length === 0){
      this.displayList.push("No record found")
    }
  }

  updateUrl() {
    const url = this.router
      .createUrlTree([window.location.pathname], {
        queryParams: {
          'filename':this.selectedFilename,
        }
      }).toString();
    this.location.go(url);
  }

  ngOnInit(): void {
    this.fileService.filename.subscribe(filename => {
      this.selectedFilename = filename;
    });
    this.loading = true;
    this.loadingError = false;
    this.service
      .getFileInfo('/fileinfo')
      .pipe(
        catchError((error: HttpErrorResponse) => {
          this.loadingError = true;
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
          this.fileList.push(fileInfo.name);
        }
        this.displayList = this.fileList;
        this.loading = false;
      });
  }

}
