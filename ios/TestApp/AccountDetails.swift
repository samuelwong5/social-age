//
//  AccountDetails.swift
//  TestApp
//
//  Created by Michael Cheung on 1/18/16.
//  Copyright © 2016 i-connect. All rights reserved.
//

import Foundation
import UIKit

class AccountDetails : UIViewController{
        
    @IBOutlet var profilePicView: UIImageView!
    @IBOutlet var nameTextLabel: UILabel!
    @IBOutlet var ageTextLabel: UILabel!
    
    var image:UIImage = UIImage()
    var name = String()
    var age = String()
    var jsonData = NSDictionary()
    
    override func viewDidLoad() {
        //Display fetched data
        nameTextLabel.text = name
        ageTextLabel.text = age
        profilePicView.image = image
    }
    
}
