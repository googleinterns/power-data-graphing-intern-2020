import { Component, OnInit} from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  data = 'Not available';

  constructor(private httpClient: HttpClient){

  }

  getMessageFromServer(){
    this.httpClient.get('http://127.0.0.1:5000/',{responseType: 'text'}).subscribe(data => {
      // console.log(data);
      this.data = data;
    })
  }

  ngOnInit(){
    this.getMessageFromServer();
  }
}