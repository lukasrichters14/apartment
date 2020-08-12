import { Component, OnInit } from '@angular/core';
import {FormControl} from "@angular/forms";
import {ApiService} from "../api.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-login-code',
  templateUrl: './login-code.component.html',
  styleUrls: ['./login-code.component.css']
})
export class LoginCodeComponent implements OnInit {
  // Error displays.
  required = false;
  errMessage: string = '';

  loginCode = new FormControl('');

  constructor(private api: ApiService, private router: Router) { }

  ngOnInit(): void {
  }

  onSubmit(): void {
    // Display required error.
    if (this.loginCode.value == ''){
      this.required = true;
      return
    }
    // Turn off required error.
    this.required = false;
    // Second stage of login.
    this.api.login('', '', this.loginCode.value)
      .subscribe(resp => {
        // If the cookie is returned from the API, the code will view that as a null value.
        if(resp != null){
          // Display the error message from the API if one occurs.
          if (resp.hasOwnProperty('error')){
            this.errMessage = resp['error'];
          }
        }
        // No error, navigate to the menu.
        else{
          // Remove any error message.
          this.errMessage = '';
          this.router.navigateByUrl('menu')
        }
      });
  }

}
