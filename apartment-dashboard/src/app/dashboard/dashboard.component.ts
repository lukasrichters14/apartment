import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  rentDue: string;

  constructor() { }

  ngOnInit(): void {
    let days = this.daysLeftInMonth();
    if (days > 1 || days == 0){
      this.rentDue = `${days} days`
    }
    else{
      this.rentDue = '1 day'
    }
  }

  /**
   * Return the days left in the current month.
   * @return
   */
  daysLeftInMonth(): number {
    let date = new Date();
    let month = date.getMonth();
    let day = date.getDate();
    let year = date.getFullYear();

    // February.
    if (month == 1){
      // Year is a leap year.
      if ((year % 4 == 0 && year % 100 != 0) || year % 400 == 0){
        return 29 - day;
      }
      return 28 - day;
    }
    // Months with 31 days.
    else if (month == 0 || month == 2 || month == 4 || month == 6 || month == 7 || month == 9 || month == 11){
      return 31 - day;
    }
    // Default is a month with 30 days.
    return 30 - day;
  }
}
