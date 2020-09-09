import { Component, OnInit } from '@angular/core';
import {ApiService} from "../api.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-menu',
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {

  constructor(private api: ApiService, private route:Router) { }

  ngOnInit(): void {
    this.api.validate(false)
      .subscribe( resp => {
        console.log(resp);
        if(resp.hasOwnProperty('error')){
          this.route.navigateByUrl('login')
        }
      });
  }

}
