import { Injectable } from '@angular/core';
import {BehaviorSubject} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FileServiceService {
  filename: BehaviorSubject<string>;
  constructor() {
            const urlParams = new URLSearchParams(window.location.search);
        const fileFromUrl = urlParams.get("filename");
        if(fileFromUrl){
          this.filename = new BehaviorSubject(fileFromUrl);
        }else{
          this.filename = new BehaviorSubject("ClockworkMapTests-testMapWear__2020-12-07T03:00:20.471Z.csv");
        }

  }

  updateFilename(newFilename: string):void{
    console.log("updating services");
    if(newFilename){
      this.filename.next(newFilename);
    }
  }

  getFilename(): string{
    return this.filename.value;
  }
}
