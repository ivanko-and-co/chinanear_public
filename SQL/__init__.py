import pymssql

class SQL():
    def __init__(self, server = '', username = '', password = '') -> None:
        self.server = server
        self.username = username
        self.password = password

        self.connect()

    def connect(self):
        self.connection = pymssql.connect(server=self.server, user=self.username, password=self.password)
        self.connection.autocommit(True)
        self.cursor = self.connection.cursor()

    def query(self, query:str, params:tuple = ()) -> any:
        if not self.connection:
            self.connect()

        try:
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
            return False


    def login(self, Email) -> list[str]:
        result = self.query(query="""SELECT Uid, Email,
                            CASE
                                WHEN Type = 'super-administrator' THEN 'administrator'
                                WHEN Type = 'service' THEN 'administrator'
                                ELSE Type
                            END AS Type, PasswordHash 
                            FROM "service_auth"."main"."User"
                            WHERE Email = %s""", params=(Email,))

        return result

    def get_uppercategory(self, localization:str) -> list[str]:
        result = self.query(query=f"""SELECT Name{localization}, NameEn, Uid FROM service_category.main.Category WHERE [Level] = 1""")
        return result

    def get_subcategory(self, localization:str, parent_category:str, level:int):
        result = self.query(query=f"SELECT Name{localization}, NameEn, Uid FROM service_category.main.Category "
                                    +"WHERE ParentUid = (SELECT Uid FROM service_category.main.Category WHERE NameEn = %s and Level = %s)",
                                    params=(parent_category, level))
        
        return result

    def get_products(self, localization:str, l3_category:str, offset:int, per_page:int):
        result = self.query(query=f"SELECT PC.Uid, PC.Name{localization}, PC.ShortDescription{localization}, PC.PreviewPhoto, PC.CostRange, PC.SellerUid, S.SellerName{localization}, PC.Stock "
                                    +"FROM service_product_card.main.ProductCard PC "
                                    +"JOIN service_actor.main.Seller S on S.Uid = PC.SellerUid " 
                                    +"WHERE ProductCategoryUid = %s AND IsActive = 1 "
                                    +"ORDER BY PC.Id OFFSET %s ROWS FETCH NEXT %s ROWS ONLY",
                                    params=(l3_category, offset, per_page))
        
        return result

    def get_category_uid(self, name, level):
        result = self.query(query="SELECT C.Uid FROM service_category.main.Category C WHERE C.NameEn  = %s AND C.[Level] = %s",
                            params=(name, level))
        
        return result

    def get_category_name(self, localization:str, categoryes:list):
        result = self.query(query=f"SELECT C.Name{localization}, C.NameEn FROM service_category.main.Category C "
                                    +"WHERE C.NameEn IN (%s, %s, %s)", params=(categoryes[0], categoryes[1], categoryes[2]))
        
        return result
    
    def get_category(self, localization:str, category):
        result = self.query(query=f"SELECT c.Name{localization} "
                                    +"FROM service_category.main.Category c "
                                    +"WHERE c.Uid = %s",
                            params=(category))
        
        return result
    
    def get_currency(self):
        result = self.query(query='SELECT CurrencyTo, Rate, MomentChangedUtc FROM service_exchange_rate.main.ExchangeRate')

        return result
    
    def get_product(self, uid:str):
        result = self.query(query="SELECT pc.Name, pc.Description, pc.ShortDescription, pc.Photos, pc.CostRange, pc.QuantityUnitSysname, pcqu.QuantityUnitName, pc.SellerUid "
                                    +"FROM service_product_card.main.ProductCard pc "
                                    +"JOIN service_product_card.main.ProductCardQuantityUnit pcqu ON pcqu.Sysname = pc.QuantityUnitSysname "
                                    +"WHERE pc.Uid = %s", params=(uid,))

        return result
    
    def get_cart(self, uid) -> list:
        result = self.query(query='SELECT CartDetails FROM service_cart.main.Cart WHERE UserCreatedUid = %s;',params=(uid,))

        return result
    
    def get_buyer_address(self, uid):
        result = self.query(query='SELECT b.BuyerAddress FROM service_actor.main.Buyer b WHERE b.Uid = (SELECT bu.BuyerUid FROM service_actor.main.BuyerUsers bu WHERE bu.UserUid = %s)',
                            params=(uid,))

        return result
    
    def get_product_cart(self, uids, localization:str):
        result = self.query(query=f"""SELECT pc.Uid, pc.Name{localization}, pc.PreviewPhoto, pc.CostRange, pc.SellerUid, s.SellerName{localization} 
                                    FROM service_product_card.main.ProductCard pc 
                                    Join service_actor.main.Seller s ON s.Uid = pc.SellerUid 
                                    WHERE pc.Uid IN {uids}""")
        
        return result
    
    def update_cart(self, cart, uid):
        result = self.query(query='UPDATE service_cart.main.Cart SET CartDetails=%s WHERE UserCreatedUid = %s;',params=(cart, uid))
        

        return result

    def insert_user(self, uid, password, email, country, type, time):
        result = self.query(query="""INSERT INTO service_auth.main.[User]
                                    (Uid, PasswordHash, Email, Country, LocaleCode, [Type], MomentCreatedUtc, UserCreatedUid)
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s);""",
                                    params=(uid, password, email, country, country, type, time, uid))
        

        return result
    
    def insert_profile(self, id_uid, fname, lname, phone, uid, time):
        result = self.query(query="""INSERT INTO service_profile.main.Profile
                                    (Uid, FirstName, LastName, PhoneNumber, LinkedUserUid, MomentCreatedUtc, UserCreatedUid)
                                    VALUES(%s, %s, %s, %s, %s, %s, %s);""",
                                    params=(id_uid, fname, lname, phone, uid, time, uid))

        return result

    def get_full_name(self, user_uid):
        result = self.query(query="SELECT (FirstName + LastName) AS Name FROM service_profile.main.Profile WHERE LinkedUserUid = %s",
                            params=(user_uid,))
        
        return result
    
    def insert_buyer_uid(self, b_uid, uid):
        result = self.query(query="""INSERT INTO service_actor.main.BuyerUsers
                                    (BuyerUid, UserUid)
                                    VALUES(%s, %s);""",
                                    params=(b_uid, uid))
        
        
        return result
    
    def insert_buyer(self, b_uid, address, name, brand, time, uid):
        result = self.query(query="""INSERT INTO service_actor.main.Buyer
                                    (Uid, BuyerAddress, BuyerDeliveryAddress, BuyerName, BuyerFullName, Brand, MomentCreatedUtc, UserCreatedUid)
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s);""",
                                    params=(b_uid, address, address, name, name, brand, time, uid))
        
        
        return result
    
    def insert_chat_user(self, uid, b_uid, time):
        result = self.query(query="""INSERT INTO service_chat.main.[User]
                                    (Uid, ActorUid, MomentCreatedUtc)
                                    VALUES(%s, %s, %s);""", 
                                    params=(uid, b_uid, time))
        
        
        return result

    def insert_user_cart(self, cart_uid, cart_details, b_uid, time, uid):
        result = self.query(query="""INSERT INTO service_cart.main.Cart
                                    (Uid, CartDetails, BuyerUid, MomentCreatedUtc, MomentUpdatedUtc, UserCreatedUid, UserUpdatedUid)
                                    VALUES(%s, %s, %s, %s, %s, %s, %s);""",
                                    params=(cart_uid, cart_details, b_uid, time, time, uid, uid))
        
        
        return result

    def create_chat_user_if_not_exists(self, user_uid, act_uid, time):
        self.query(query="""IF NOT EXISTS (
                                SELECT Uid FROM "service_chat"."main"."User"
                                WHERE Uid = %s
                            )
                            BEGIN
                                INSERT INTO "service_chat"."main"."User" ("Uid", "ActorUid", "MomentCreatedUtc") VALUES (%s, %s, %s);
                            END;""",
                    params=(user_uid, user_uid, act_uid, time))

    def init_chat_room(self, user_uid, act_uid, user_uid2, act_uid2, time, chat_uid):
        '''Создаёт чат между двумя пользователями если его ещё не существует'''
        self.create_chat_user_if_not_exists(user_uid, act_uid, time)
        self.create_chat_user_if_not_exists(user_uid2, act_uid2, time)
        result = self.query(query="""IF NOT EXISTS (
                                        SELECT ChatRoomUid FROM "service_chat"."main"."ChatRoomUser"
                                        WHERE UserUid = %s
                                        AND ChatRoomUid IN (
                                            SELECT ChatRoomUid FROM "service_chat"."main"."ChatRoomUser" WHERE UserUid = %s
                                        )
                                    )
                                    BEGIN
                                        INSERT INTO "service_chat"."main"."ChatRoom" ("Uid", "MomentCreatedUtc") VALUES (%s, %s);
                                        INSERT INTO "service_chat"."main"."ChatRoomUser" ("ChatRoomUid", "UserUid", "ActorUid") VALUES (%s, %s, %s);
                                        INSERT INTO "service_chat"."main"."ChatRoomUser" ("ChatRoomUid", "UserUid", "ActorUid") VALUES (%s, %s, %s);
                                    END;""",
                            params=(user_uid, user_uid2, chat_uid, time, chat_uid, user_uid, act_uid, chat_uid, user_uid2, act_uid2))
        
        
        return result

    def add_admin_to_chat(self, chat_uid, admin_uid):
        self.query(query='INSERT INTO "service_chat"."main"."ChatRoomUser" ("ChatRoomUid", "UserUid") VALUES (%s, %s);',
                   params=(chat_uid, admin_uid))

    def get_chat_uid(self, user_uid, user_uid2):
        result = self.query(query="""SELECT chat1.ChatRoomUid FROM service_chat.main.ChatRoomUser AS chat1
                                    LEFT JOIN service_chat.main.ChatRoomUser AS chat2 ON chat1.ChatRoomUid = chat2.ChatRoomUid
                                    WHERE chat1.UserUid = %s AND chat2.UserUid = %s
                                    AND chat1.ActorUid IS NOT NULL AND chat2.ActorUid IS NOT NULL""",
                            params=(user_uid, user_uid2))
        return result

    def load_chat(self, chat_uid):
        result = self.query(query="""SELECT msg.SenderUid, msg.Payload, msg.ActorUid, (p.FirstName + ' ' + p.LastName) AS Name
                                    FROM service_chat.main.ChatRoomMessage AS msg
                                    LEFT OUTER JOIN service_profile.main.Profile as p ON p.LinkedUserUid = msg.SenderUid
                                    WHERE msg.ChatRoomUid = %s
                                    ORDER BY msg.MomentCreatedUtc ASC""",
                            params=(chat_uid,))
        return result

    def get_actor_uid(self, user_uid, role) -> str:
        try:
            if role == 'buyer':
                return self.query(query="""SELECT BuyerUid FROM "service_actor"."main"."BuyerUsers" WHERE UserUid = %s;""",
                                params=(user_uid,))[0][0]
            elif role == 'seller':
                return self.query(query="""SELECT SellerUid FROM "service_actor"."main"."SellerUsers" WHERE UserUid = %s;""",
                                params=(user_uid,))[0][0]
            elif role == 'administrator':
                return self.query(query="""SELECT AdminUid FROM "service_actor"."main"."AdminUsers" WHERE UserUid = %s;""",
                                params=(user_uid,))[0][0]
        except:
            return ''
    
    def get_user_uid(self, actor_uid, role) -> str:
        try:
            if role == 'buyer':
                return self.query(query="""SELECT UserUid FROM "service_actor"."main"."BuyerUsers" WHERE BuyerUid = %s;""",
                                params=(actor_uid,))[0][0]
            elif role == 'seller':
                return self.query(query="""SELECT UserUid FROM "service_actor"."main"."SellerUsers" WHERE SellerUid = %s;""",
                                params=(actor_uid,))[0][0]
            elif role == 'administrator':
                return self.query(query="""SELECT UserUid FROM "service_actor"."main"."AdminUsers" WHERE AdminUid = %s;""",
                                params=(actor_uid,))[0][0]
        except:
            return ''
        
    def insert_offer(self, offer_uid, order_uid, offers_details, price, time, uid_create, status):
        result = self.query(query="INSERT INTO service_order.main.Offer"
                                    +"(Uid, OrderUid, OfferDetails, TotalPrice, MomentCreatedUtc, UserCreatedUid, State)"
                                    +"VALUES(%s, %s, %s, %s, %s, %s, %s);",
                                    params=(offer_uid, order_uid, offers_details, price, time, uid_create, status))

        return result


    def insert_order(self, order_uid, s_uid, b_uid, b_note, address, offer_uid, create_time, status):
        result = self.query(query="INSERT INTO service_order.main.[Order]"
                                    +"(Uid, OrderNumber, SellerUid, BuyerUid, BuyerNote, Address, InitialOfferUid, OfferUid, MomentCreatedUtc, StateSysName) "
                                    +"VALUES(%s, (SELECT "
                                    +"CASE "
                                    +"	WHEN MAX(OrderNumber) IS NULL THEN 1 "
                                    +"	ELSE MAX(CAST(OrderNumber AS INT)) + 1 "
                                    +"END FROM service_order.main.[Order]), "
                                    +"%s, %s, %s, %s, %s, %s, %s, %s);",
                            params=(order_uid, s_uid, b_uid, b_note, address, offer_uid, offer_uid, create_time, status))
        
        return result

    def insert_order_history(self, uid, time, o_uid, old_statrus, new_status):
        result = self.query(query="INSERT INTO service_order.main.OrderStateHistory "
                                    +"(UserUid, Moment, OrderUid, FromState, ToState) "
                                    +"VALUES(%s, %s, %s, %s, %s);",
                            params=(uid, time, o_uid, old_statrus, new_status))

        return result

    def update_order_state(self, state, time, order_number, uid):
        result = self.query(query="UPDATE service_order.main.Offer ofe "
                                    +"SET ofe.State = %s, ofe.MomentStateTransitionUtc = %s, ofe.UserUpdatedUid = %s "
                                    +"WHERE ofe.Uid = (SELECT o.OfferUid FROM service_order.main.[Order] o WHERE o.OrderNumber = %s); "
                                    +"UPDATE service_order.main.[Order] "
                                    +"SET StateSysName = %s, MomentUpdatedUtc = %s, UserUpdatedUid = %s "
                                    +"WHERE OfferUid = %s;",
                                    params=(state, time, uid, order_number, state, time, uid, order_number))

        return result
    
    def get_orders_buyer(self, uid, localization, offset:int = 0, status:str = '%', min_date:str = '2000-01-01', max_date:str = '2200-01-01'):
        if localization == 'Ru':
            result = self.query(query=f"SELECT o.OrderNumber, os.Name, o.MomentCreatedUtc, o.MomentUpdatedUtc, s.SellerName{localization}, ofe.OfferDetails "
                                    +"FROM service_order.main.[Order] o "
                                    +"JOIN service_order.main.Offer ofe ON ofe.OrderUid = o.Uid "
                                    +"JOIN service_actor.main.Seller s ON s.Uid = o.SellerUid "
                                    +"JOIN service_order.main.OrderState os ON os.[SysName] = o.StateSysName "
                                    +"WHERE o.BuyerUid = (SELECT bu.BuyerUid FROM service_actor.main.BuyerUsers bu WHERE bu.UserUid = %s) "
                                    +"AND o.StateSysName LIKE %s AND o.MomentCreatedUtc >= %s AND o.MomentCreatedUtc <= %s "
                                    +"ORDER BY o.Id OFFSET %s ROWS FETCH NEXT 15 ROWS ONLY",
                                    params=(uid, status, min_date, max_date, offset))
        else:
            result = self.query(query=f"SELECT o.OrderNumber, o.StateSysName, o.MomentCreatedUtc, o.MomentUpdatedUtc, s.SellerName{localization}, ofe.OfferDetails "
                                    +"FROM service_order.main.[Order] o "
                                    +"JOIN service_order.main.Offer ofe ON ofe.OrderUid = o.Uid "
                                    +"JOIN service_actor.main.Seller s ON s.Uid = o.SellerUid "
                                    +"WHERE o.BuyerUid = (SELECT bu.BuyerUid FROM service_actor.main.BuyerUsers bu WHERE bu.UserUid = %s) "
                                    +"AND o.StateSysName LIKE %s AND o.MomentCreatedUtc >= %s AND o.MomentCreatedUtc <= %s "
                                    +"ORDER BY o.Id OFFSET %s ROWS FETCH NEXT 15 ROWS ONLY",
                                    params=(uid, status, min_date, max_date, offset))
        
        return result
    
    def get_order(self, order_number, localization):
        result = self.query(query=f"SELECT s.SellerName{localization}, o.Address, ofe.OfferDetails, ofe.TotalPrice, os.Name "
                                    +"FROM service_order.main.[Order] o "
                                    +"JOIN service_actor.main.Seller s ON s.Uid = o.SellerUid "
                                    +"JOIN service_order.main.Offer ofe ON ofe.OrderUid = o.Uid "
                                    +"JOIN service_order.main.OrderState os ON os.[SysName] = ofe.State "
                                    +"WHERE o.OrderNumber = %s;",
                                    params=(order_number))
        
        return result
    
    def get_orders_count(self, user_uid):
        result = self.query(query="""SELECT COUNT(o.Uid) FROM service_order.main.[Order] AS o
                                    JOIN service_actor.main.BuyerUsers AS bu ON bu.UserUid = %s 
                                    WHERE o.BuyerUid = bu.BuyerUid""",
                            params=(user_uid,))
        return result
    
    def get_order_product(self, product_uids, localization):
        result = self.query(query=f"SELECT pc.Uid, pc.PreviewPhoto, pc.Name{localization} "
                                    +"FROM service_product_card.main.ProductCard pc "
                                    +f"WHERE pc.Uid IN {product_uids};")
        
        return result

    def search_seller(self, search_text, localization):
        search_text = '%' + search_text + '%'
        result = self.query(query=f"SELECT SellerName{localization}, Uid FROM service_actor.main.Seller WHERE SellerName{localization} LIKE %s",
                            params=(search_text,))
        return result

    def search_product_and_img(self, search_text, localization):
        search_text = '%' + search_text + '%'
        result = self.query(query=f"SELECT Name{localization}, PreviewPhoto, Uid FROM service_product_card.main.ProductCard WHERE Name{localization} "
                                    +"LIKE %s AND IsActive = '1' AND ProductCategoryUid IS NOT NULL ORDER BY Id OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY",
                            params=(search_text,))
        return result

    def get_product_url_by_uid(self, uid):
        result = self.query(query="SELECT c1.NameEn, c2.NameEn, c3.NameEn, pc.Uid "
                                    +"FROM service_product_card.main.ProductCard AS pc "
                                    +"JOIN service_category.main.Category AS c3 ON pc.ProductCategoryUid = c3.Uid "
                                    +"JOIN service_category.main.Category AS c2 ON c3.ParentUid = c2.Uid "
                                    +"JOIN service_category.main.Category AS c1 ON c2.ParentUid = c1.Uid "
                                    +"WHERE pc.Uid = %s",
                            params=(uid,))
        return result
    
    def update_currency(self, to_currency, value, time):
        result = self.query(query="UPDATE service_exchange_rate.main.ExchangeRate "
                                    +"SET Rate=%s, MomentChangedUtc=%s "
                                    +"WHERE CurrencyTo=%s",
                            params=(value, time, to_currency))
        
        return result
    
    def get_current_password_reset(self, email):
        result = self.query(query="""SELECT usr.Uid, ml.IsUsed FROM service_auth.main.[User] AS usr
                                    LEFT JOIN service_auth.main.MagicLink AS ml ON ml.LinkedUserUid = usr.Uid 
                                    AND ml.ActionType = 'PasswordReset' AND ml.ExpiredMomentUtc > GETUTCDATE()
                                    WHERE usr.email = %s""",
                            params=(email,))
        return result
    
    def create_password_reset(self, user_uid, reset_uid, cur_date, expire_date):
        self.query(query="""INSERT INTO "service_auth"."main"."MagicLink" 
                            ("Uid", "LinkedUserUid", "ExpiredMomentUtc", "IsUsed", "ActionType", "MomentCreatedUtc") 
                            VALUES (%s, %s, %s, 0, 'PasswordReset', %s);""",
                    params=(reset_uid, user_uid, expire_date, cur_date))
        
    def verify_password_reset(self, token):
        result = self.query(query="""SELECT LinkedUserUid FROM service_auth.main.MagicLink 
                                    WHERE Uid = %s AND ExpiredMomentUtc > GETUTCDATE() AND IsUsed = 0""",
                            params=(token,))
        return result
    
    def finish_password_reset(self, token):
        self.query(query="UPDATE service_auth.main.MagicLink SET IsUsed = '1' WHERE Uid = %s",
                   params=(token,))
        
    def change_password(self, user_uid, new_password):
        self.query(query="UPDATE service_auth.main.[User] SET PasswordHash = %s WHERE Uid = %s",
                   params=(new_password, user_uid))

    def get_product_lk(self, uid, category1, category2, category3, localization):
        if category3 != '%':
            query_filter = 'JOIN service_category.main.Category AS c3 ON c3.NameEn = %s AND [Level] = 3 '
            _params = (uid, category3)
        elif category2 != '%':
            query_filter = 'JOIN service_category.main.Category AS c2 ON c2.NameEn = %s AND [Level] = 2 '
            query_filter += 'JOIN service_category.main.Category AS c3 ON c3.ParentUid = c2.Uid '
            _params = (uid, category2)
        elif category1 != '%':
            query_filter = 'JOIN service_category.main.Category AS c1 ON c1.NameEn = %s '
            query_filter += 'JOIN service_category.main.Category AS c2 ON c2.ParentUid = c1.Uid '
            query_filter += 'JOIN service_category.main.Category AS c3 ON c3.ParentUid = c2.Uid '
            _params = (uid, category1)
        else:
            query_filter = 'JOIN service_category.main.Category AS c3 ON c3.[Level] = 3 '
            _params = (uid)

        result = self.query(query=f"SELECT pc.Uid, pc.PreviewPhoto, pc.ShortDescription{localization}, pc.Stock, pc.ProductCategoryUid, "
                                    +"CASE "
                                    +"	WHEN pc.MomentUpdatedUtc = NULL THEN pc.MomentCreatedUtc "
                                    +"	ELSE pc.MomentUpdatedUtc "
                                    +"END AS 'MomentUpdatedUtc', pc.IsActive, pc.CostRange "
                                    +"FROM service_product_card.main.ProductCard pc "
                                    +"JOIN service_actor.main.SellerUsers su ON su.UserUid = %s "
                                    +query_filter
                                    +"WHERE pc.SellerUid = su.SellerUid AND pc.ProductCategoryUid = c3.Uid",
                                    params=_params)

        return result
    
    def get_count_product(self, l3_category_uid):
        result = self.query(query="SELECT COUNT(*) FROM service_product_card.main.ProductCard pc "
                                    +"WHERE pc.ProductCategoryUid = %s AND IsActive = 1",
                            params=(l3_category_uid))
        return result
    
    def insert_product(self, product_uid, is_active, stock, time, name, description, short_description, photos, preview_photo,
                       product_category_uid, cost_range, quantity_sysname, seller_uid, uid):
        result = self.query(query="INSERT INTO service_product_card.main.ProductCard "
                                    +"(Uid, IsActive, Stock, MomentActiveStatusChangeUtc, Name, Description, ShortDescription, "
                                    +"Photos, PreviewPhoto, ProductCategoryUid, CostRange, QuantityUnitSysname, SellerUid, "
                                    +"MomentCreatedUtc, MomentUpdatedUtc, UserCreatedUid, UserUpdatedUid) "
                                    +"VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            params=(product_uid, is_active, stock, time, name, description, short_description, photos, preview_photo, 
                                    product_category_uid, cost_range, quantity_sysname, seller_uid, time, time, uid, uid))
        
        return result
    
    def update_product(self, data):
        result = self.query(query="UPDATE service_product_card.main.ProductCard "
                                    +f"SET {data[0]} "
                                    +"WHERE Uid = %s",
                            params=data[0])
        
        return result
    
    def get_buyer_info(self, uid):
        result = self.query(query="SELECT b.Uid, b.BuyerAddress, b.BuyerName, b.BuyerFullName, b.Brand "
                                    +"FROM service_actor.main.Buyer b "
                                    +"WHERE b.Uid = %s",
                            params=(uid))
        
        return result
    
    def insert_seller_user(self, seller_info):
        result = self.query(query="INSERT INTO service_actor.main.Seller "
                                    +"(Uid, SellerAddress, SellerName, SellerFullName, Brand, MomentCreatedUtc, UserCreatedUid) "
                                    +"VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            params=(seller_info[0], seller_info[1], seller_info[2], seller_info[3], seller_info[4], seller_info[5], seller_info[6]))

        return result

    def insert_seller_user_link(self, u_uid, s_uid):
        result = self.query(query="INSERT INTO service_actor.main.SellerUsers "
                                    +"(SellerUid, UserUid) "
                                    +"VALUES(%s, %s);",
                            params=(s_uid, u_uid))
        
        return result

    def update_user_status(self, type, time, user_uid):
        result = self.query(query="UPDATE service_auth.main.[User] "
                                    +"SET [Type] = %s, MomentUpdatedUtc = %s "
                                    +"WHERE Uid = %s",
                            params=(type, time, user_uid))
        
        return result
    
    def get_product_units(self):
        result = self.query(query="SELECT pcqu.[Sysname], pcqu.QuantityUnitName "
                                    +"FROM service_product_card.main.ProductCardQuantityUnit pcqu")
        
        return result
    
    def update_offer(self, time, uid, state, order_number):
        result = self.query(query="UPDATE service_order.main.Offer "
                                    +"SET MomentUpdatedUtc=%s, UserUpdatedUid=%s, State=%s "
                                    +"WHERE OrderUid = (SELECT Uid FROM service_order.main.[Order] o WHERE o.OrderNumber = %s)",
                            params=(time, uid, state, order_number))
        
        return result
    
    def update_order(self, time, uid, status, order_number):
        result = self.query(query="UPDATE service_order.main.[Order] "
                                    +"SET MomentUpdatedUtc=%s, UserUpdatedUid=%s, StateSysName=%s "
                                    +"WHERE OrderNumber = %s",
                            params=(time, uid, status, order_number))
        
        return result
    
    def get_product_change(self, uid, product_uid):
        result = self.query(query="SELECT pc.Uid, pc.IsActive, pc.Stock, pc.Name, pc.Description, pc.ShortDescription, pc.Photos, pc.PreviewPhoto, "
                                    +"pc.CostRange, pc.QuantityUnitSysname, c1.[Sysname], c2.[Sysname], c3.[Sysname] "
                                    +"FROM service_product_card.main.ProductCard pc "
                                    +"JOIN service_category.main.Category c3 ON c3.Uid = pc.ProductCategoryUid "
                                    +"JOIN service_category.main.Category c2 ON c2.Uid = c3.ParentUid "
                                    +"JOIN service_category.main.Category c1 ON c1.Uid = c2.ParentUid "
                                    +"JOIN service_actor.main.SellerUsers su ON su.UserUid = %s "
                                    +"WHERE pc.Uid = %s AND pc.SellerUid = su.SellerUid",
                            params=(uid, product_uid))
        
        return result[0]