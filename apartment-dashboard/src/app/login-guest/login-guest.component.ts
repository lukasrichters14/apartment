import { Component, OnInit } from '@angular/core';
import {FormControl} from "@angular/forms";
import {ApiService} from "../api.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-login-guest',
  templateUrl: './login-guest.component.html',
  styleUrls: ['./login-guest.component.css']
})
export class LoginGuestComponent implements OnInit {
  // Error displays.
  required = false;
  errMessage: string = '';

  guestName = new FormControl('');

  constructor(private api: ApiService, private router: Router) { }

  ngOnInit(): void {
  }

  onSubmit(): void {
    if(this.guestName.value == ''){
      this.required = true;
      return
    }
    // Turn off required error.
    this.required = false;
    this.api.login(this.guestName.value)
      .subscribe(resp =>{
        // Display the error message from the API if one occurs.
        if (resp.hasOwnProperty('error')){
          this.errMessage = resp['error'];
        }
        // No error, navigate to the menu.
        else {
          // Remove any error message.
          this.errMessage = '';
          this.router.navigateByUrl('menu')
        }
      });
  }

}
